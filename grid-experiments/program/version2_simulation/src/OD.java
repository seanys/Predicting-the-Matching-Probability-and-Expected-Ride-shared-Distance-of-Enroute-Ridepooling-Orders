package version2_simulation;

import java.util.*;

public class OD {
	double[] origin;
	double[] destination;
	double rate;
	
	List<Order> orders_waiting;
	List<Order> orders_traveling;
	
	int total_num;
	int leave_num;
	int seeker_num;
	int taker_waiting_num;
	int taker_traveling_num;
	int total_matched_num;
	
	double total_traveling_distance;
	double total_shared_distance;
	double total_saved_distance;
	
	public OD(double[] origin, double[] destination, double rate){
		this.origin = origin.clone();
		this.destination = destination.clone();
		this.rate = rate;
		
		this.total_num = 0;
		this.leave_num = 0;
		this.seeker_num = 0;
		this.taker_waiting_num = 0;
		this.taker_traveling_num = 0;
		
		this.total_traveling_distance = 0;
		this.total_shared_distance = 0;
		this.total_saved_distance = 0;
		
		this.orders_waiting = new ArrayList<>();
		this.orders_traveling = new ArrayList<>();
	}
	
	//get the arrival time interval between the current order and the next one according to the predetermined rate
	public double get_next_order_time_interval(){
		Random rand = new Random();
		double temp = rand.nextDouble();
		double interval = - Math.log(temp)/this.rate;
		return interval;
	}
}
