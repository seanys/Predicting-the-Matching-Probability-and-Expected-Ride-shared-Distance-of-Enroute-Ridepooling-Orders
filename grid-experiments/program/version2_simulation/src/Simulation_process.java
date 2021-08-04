package version2_simulation;

import java.util.Comparator;
import java.util.Date;
import java.util.List;
import java.util.PriorityQueue;
import java.util.Random;

public class Simulation_process {
	double maximum_matching_radius;
	double pick_up_waiting_time;
	double maximum_detour_time;
	double scale;
	
	double current_time;
	double total_running_time;
	double start_record_time;
	Date start_date;
	
	Tool tool;
	IO io;
	
	List<OD> od_list;
	PriorityQueue<Event> queue = new PriorityQueue<>(event_time_comparator);
	
	//input filenames
	String od_filename;
	
	//output filename
	String od_w_filename;
	
	
	public Simulation_process(double maximum_matching_radius, double pick_up_waiting_time, double maximum_detour_time, double scale){
		this.maximum_matching_radius = maximum_matching_radius;
		this.pick_up_waiting_time = pick_up_waiting_time;
		this.maximum_detour_time = maximum_detour_time;
		this.scale = scale;
		
		this.tool = new Tool(this.maximum_matching_radius, this.maximum_detour_time);
	}
	
	public static Comparator<Event> event_time_comparator = new Comparator<Event>(){
		public int compare(Event e1, Event e2){
			if(e1.time - e2.time > 0){
				return 1;
			}else if(e1.time == e2.time){
				return 0;
			}else{
				return -1;
			}
		}
	};
	
	public void initialize_queue(){
		for(OD od : this.od_list){
			double arrival_time = od.get_next_order_time_interval();
			Event e = new Event(0, arrival_time, null, od);
			this.queue.add(e);
		}
	}
	
	public void initialize_simulation(){
		this.current_time = 0;
		this.io = new IO(this.scale);
		this.io.od_filename = this.od_filename;
		this.io.od_w_filename = this.od_w_filename;
		this.io.readOD();
		this.od_list = this.io.od_list;		
		initialize_queue();		
	}
	
	public void simulate(){
		while(true){
			Event event = this.queue.poll();
			this.current_time = event.time;
			int event_type = event.type;
			
			if(this.current_time >= this.total_running_time){
				Date end_date = new Date();
				long running_duration = end_date.getTime() - this.start_date.getTime();
				this.io.write_OD(running_duration);
				return;
			}
			
			if(event_type == 0){
				handle_event_type0(event);
			}else{
				Order order = event.order;
				if(order.status == 1){
					//this order has already been matched
					OD od = order.od;
					int order_phase = order.phase;
					if(this.current_time >= this.start_record_time){
						if(order_phase == 1){
							od.taker_waiting_num = od.taker_waiting_num + 1;
						}else{
							od.taker_traveling_num = od.taker_traveling_num + 1;
						}
					}
					if(order_phase == 1){
						od.orders_waiting.remove(order);
					}else{
						od.orders_traveling.remove(order);
					}
				}else{
					if(event_type == 1){
						handle_event_type1(event);
					}else{
						handle_event_type2(event);
					}
				}
			}
		}
	}
	
	public void handle_event_type0(Event event){
		OD od = event.od;
		
		//first add a new order event to the queue
		double arrival_time = od.get_next_order_time_interval();
		Event event_next_order = new Event(0, event.time + arrival_time, null, od);
		this.queue.add(event_next_order);
		
		//since the pick up time may not be a constant, here it is treated as a random variable following
		//Gaussian distribution with mean = pick_up_waiting_time, standard error = 1/6 * mean
		//In addition, since no pick up time could be negative, the generated pick up time is set to greater than error = 1/6 * mean
		Random rand = new Random();
		double num = rand.nextGaussian();
		double generated_pick_up_time = 1.0/6.0 *this.pick_up_waiting_time + this.pick_up_waiting_time;
		
		//Order order = new Order(od.origin.clone(), 0, od, event.time, 0, generated_pick_up_time);
		Order order = new Order(od.origin.clone(), 0, od, event.time, 0, this.pick_up_waiting_time);
		
		if(this.current_time >= this.start_record_time){
			od.total_num = od.total_num + 1;
		}
		
		//check whether the order could be matched with someone waiting in the origin of the same od pair
		List<Order> orders_waiting = od.orders_waiting;
		for(Order orderi : orders_waiting){
			if(orderi.status == 0){
				orderi.status = 1;
				
				if(this.current_time >= this.start_record_time){
					od.seeker_num = od.seeker_num + 1;
					double[] returns = tool.get_match_kpi_between_orders(order, orderi);
					tool.update_od_kpi_after_matching_for_two_orders(order, orderi, returns);
				}
				return;
			}
		}
		
		//check whether the order could be matched with someone waiting in their origins from other od pairs
		double min_pick_up_time = 10000;
		boolean flag_matching = false;
		Order order_matching = null;
		for(OD odi : this.od_list){
			List<Order> orders_waiting_odi = odi.orders_waiting;
			for(Order orderi : orders_waiting_odi){
				if(orderi.status == 0){
					double[] returns = tool.get_match_kpi_between_orders(order, orderi);
					if(returns[0] > 0){
						flag_matching = true;
						double pick_up_time = tool.get_traveling_time(order.position, orderi.position);
						if(pick_up_time < min_pick_up_time){
							min_pick_up_time = pick_up_time;
							order_matching = orderi;
						}
					}
				}
			}
			
			List<Order> orders_traveling_odi = odi.orders_traveling;
			for(Order orderi : orders_traveling_odi){
				if(orderi.status == 0){
					orderi.set_position(this.current_time);
					double[] returns = tool.get_match_kpi_between_orders(order, orderi);
					if(returns[0] > 0){
						flag_matching = true;
						double pick_up_time = tool.get_traveling_time(order.position, orderi.position);
						if(pick_up_time < min_pick_up_time){
							min_pick_up_time = pick_up_time;
							order_matching = orderi;
						}
					}
				}
			}
		}
		
		if(flag_matching == true){
			order.status = 1;
			order_matching.status = 1;
			if(this.current_time >= this.start_record_time){
				od.seeker_num = od.seeker_num + 1;
				double[] returns = tool.get_match_kpi_between_orders(order, order_matching);
				tool.update_od_kpi_after_matching_for_two_orders(order, order_matching, returns);
				
				if(order_matching.phase == 1){
					order_matching.od.taker_waiting_num = order_matching.od.taker_waiting_num + 1;				
				}else{
					order_matching.od.taker_traveling_num = order_matching.od.taker_traveling_num + 1;					
				}
			}
			
			//delete order_matching from its current order list
			if(order_matching.phase == 1){
				order_matching.od.orders_waiting.remove(order_matching);				
			}else{
				order_matching.od.orders_traveling.remove(order_matching);				
			}
			
			return;
		}
		
		//unmatched
		Event event_next = new Event(1, event.time + order.waiting_time, order, od);
		this.queue.add(event_next);
		order.phase = 1;
		od.orders_waiting.add(order);
	}

	public void handle_event_type1(Event event){
		//some passenger is picked up by a car and leaving his origin
		Order order = event.order;
		OD od = event.od;
		if(order.status == 1){
			if(this.current_time > this.start_record_time){
				od.taker_waiting_num = od.taker_waiting_num + 1;
			}
			od.orders_waiting.remove(order);
		}
		order.phase = 2;		
		od.orders_waiting.remove(order);
		od.orders_traveling.add(order);
		
		double whole_od_length = tool.get_traveling_time(od.origin, od.destination);
		Event event_next = new Event(2, this.current_time + whole_od_length, order, od);
		this.queue.add(event_next);
	}
	
	public void handle_event_type2(Event event){
		OD od = event.od;
		Order order = event.order;
		
		if(this.current_time >= this.start_record_time){
			od.leave_num = od.leave_num + 1;
			
			double whole_route_length = tool.get_traveling_time(od.origin, od.destination);
			od.total_traveling_distance = od.total_traveling_distance + whole_route_length;
		}
		od.orders_traveling.remove(order);
	}
}
