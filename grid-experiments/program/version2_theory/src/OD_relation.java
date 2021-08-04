package version2_theory;

import java.util.Comparator;
import java.util.List;
import java.util.PriorityQueue;

public class OD_relation {
	double maximum_matching_radius;
	double pick_up_waiting_time;
	double maximum_detour_time;
	
	List<OD> od_list;
	
	public OD_relation(double maximum_matching_radius, double pick_up_waiting_time, double maximum_detour_time, List<OD> od_list){
		this.maximum_matching_radius = maximum_matching_radius;
		this.pick_up_waiting_time = pick_up_waiting_time;
		this.maximum_detour_time = maximum_detour_time;
		this.od_list = od_list;
		
		for(int k = 0; k < od_list.size(); k ++){
			route_first_node_match(k);
		}
	}
	
	public void route_first_node_match(int od_index){
		Tools tool = new Tools(this.maximum_matching_radius, this.maximum_detour_time);
		PriorityQueue<Match> match_heap=new PriorityQueue<Match>(idComparator);
		Node node = od_list.get(od_index).node_list.get(0);
		
		for(int odi = 0; odi < od_list.size(); odi ++){
			OD od_temp = od_list.get(odi);
			for(int nodej = 0; nodej < od_temp.node_list.size(); nodej ++){
				Node node_temp = od_temp.node_list.get(nodej);
				double[] returns = tool.get_shared_save_distance(node, node_temp);
				if(returns[0] >= 0){
					Match match_temp = new Match(node, node_temp, returns[0], returns[1], returns[2], returns[3]);
					match_heap.add(match_temp);		
				}
			}
		}
		
		while(match_heap.size() > 0){
			Match match_temp1 = match_heap.poll();
			Node node_temp1 = match_temp1.node1;
			Node node_temp2 = match_temp1.node2;
			node_temp1.matches.add(match_temp1);
			node_temp2.matches.add(match_temp1);
		}
	}
	
	public static Comparator<Match> idComparator = new Comparator<Match>(){
		public int compare(Match match1, Match match2){
			if(match1.current_matching_radius<=match2.current_matching_radius){
				return -1;
			}else{
				return 1;
			}
		}
	};
}
