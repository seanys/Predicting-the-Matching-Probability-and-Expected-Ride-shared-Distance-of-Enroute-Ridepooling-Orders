package version2_theory;

import java.util.Date;
import java.util.List;

public class Process {
	List<OD> od_list;
	boolean flag_termination;
	double current_maximum_gap;
	
	//parameter
	double tolerance;
	
	//result
	int iteration_number;
	long running_duration;
	
	public Process(List<OD> od_list, double tolerance){
		this.od_list = od_list;
		this.flag_termination = false;
		this.current_maximum_gap = 0;
		this.tolerance = tolerance;
		
		this.iteration_number = 0;
		this.running_duration = 0;
	}
	
	public void iteration(){
		Date date1 = new Date();
		
		while(!this.flag_termination){
			this.current_maximum_gap = 0;
			
			for(int odi = 0; odi < this.od_list.size(); odi ++){
				route_arrival_rate(odi);
			}
			for(int odi = 0; odi < this.od_list.size(); odi ++){
				route_having_passenger(odi);
			}
			
			//initialize matching rate for every OD pair
			for(int odi = 0; odi < this.od_list.size(); odi ++){
				OD od_temp = this.od_list.get(odi);
				Node first_node_temp = od_temp.node_list.get(0);
				List<Match> matches_temp = first_node_temp.matches;
				for(Match match_temp : matches_temp){
					match_temp.matching_rate = 0;
				}
			}
			
			for(int odi = 0; odi < this.od_list.size(); odi ++){
				route_match_matching_rate(odi);
			}
			
			for(int odi = 0; odi < this.od_list.size(); odi ++){
				probability(odi);
			}
			
			this.iteration_number = this.iteration_number + 1;
			if(this.current_maximum_gap <= this.tolerance){
				this.flag_termination = true;
			}
			
			if(this.iteration_number > 5000){
				break;
			}
		}
		
		Date date2 = new Date();
		long time = date2.getTime() - date1.getTime();
		this.running_duration = time;
	}
	
	//update arrival_rate for each node
	public void route_arrival_rate(int od_index){
		OD od=od_list.get(od_index);
		double od_lambda=od.rate;
		List<Node> node_list=od.node_list;
		node_list.get(0).arrival_rate=od_lambda;
		double possibility=1.0;
		possibility=possibility*(1-node_list.get(0).possibility);
		for(int i=1;i<node_list.size();i++){
			Node node_t=node_list.get(i);
			node_t.arrival_rate=od_lambda*possibility;
			possibility=possibility*(1-node_t.possibility);
		}
	}
	
	//update having_possibility for each node
	public void route_having_passenger(Node node){
		double old_possibility=node.having_possibility;//for check termination conditions
		
		double arrival_rate=node.arrival_rate;
		double matching_rate=node.matching_rate;
		double time=node.time;
		if(matching_rate==0){
			node.having_possibility=0;
		}else{
			node.having_possibility=arrival_rate*(1-Math.exp(-matching_rate*time))/matching_rate;
		}
		
		double absolute_gap = Math.abs(node.having_possibility-old_possibility);
		if(absolute_gap < this.current_maximum_gap){
			this.current_maximum_gap = absolute_gap;
		}
	}
	
	//update having_possibility for one OD pair
	public void route_having_passenger(int od_index){
		OD od=od_list.get(od_index);
		List<Node> node_list=od.node_list;
		for(int i=0;i<node_list.size();i++){
			Node node=node_list.get(i);
			if(node.type==0){
				node.having_possibility=0.0;
			}else{
				route_having_passenger(node);
			}
		}
	}
	
	//update matching rate for each match
	public void route_match_matching_rate(int od_index){
		Node first_node = this.od_list.get(od_index).node_list.get(0);
		List<Match> matches_temp = first_node.matches;
		
		if(matches_temp.size() == 0){
			return;
		}
		double od_rate = this.od_list.get(od_index).rate;
		double probability = 1.0;
		for(int matchi = 0; matchi < matches_temp.size(); matchi ++){
			Match match_temp = matches_temp.get(matchi);
			Node node2_temp = match_temp.node2;
			match_temp.matching_rate = od_rate * probability;
			probability = probability * (1 - node2_temp.having_possibility);
		}
	}
	
	//update matching_probability for nodes with type 0
	public void probability_type0(Node node0){
		double old_possibility = node0.possibility;
		
		List<Match> matches_temp = node0.matches;
		if(matches_temp.size() == 0){
			node0.possibility = 0;
			return;
		}
		double temp = 1.0;
		for(Match match_temp : matches_temp){
			Node node2_temp = match_temp.node2;
			temp = temp * (1 - node2_temp.having_possibility);
		}
		node0.possibility = 1 - temp;
		
		double absolute_error = Math.abs(old_possibility-node0.possibility);
		if(absolute_error > this.current_maximum_gap){
			this.current_maximum_gap = absolute_error;
		}
	}
	
	public void probability_type1(Node node1){
		double old_possibility = node1.possibility;
		
		double matching_rate = 0;
		for(Match match : node1.matches){
			matching_rate = matching_rate + match.matching_rate;
		}
		node1.matching_rate = matching_rate;
		
		double traveling_time = node1.time;
		double probability = 1-Math.exp(-matching_rate*traveling_time);
		node1.possibility = probability;
		
		double absolute_error = Math.abs(old_possibility-node1.possibility);
		if(absolute_error > this.current_maximum_gap){
			this.current_maximum_gap = absolute_error;
		}
	}
	
	public void probability(int od_index){
		OD od_temp = this.od_list.get(od_index);
		Node first_node = od_temp.node_list.get(0);
		probability_type0(first_node);
		for(Node nodei : od_temp.node_list){
			if(nodei.type == 0){
				continue;
			}else if(nodei.type == 1){
				probability_type1(nodei);
			}
		}
	}
}
