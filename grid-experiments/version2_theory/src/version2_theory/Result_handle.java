package version2_theory;

import java.util.List;

public class Result_handle {
	List<OD> od_list;
	
	public Result_handle(List<OD> od_list){
		this.od_list = od_list;
		for(OD odi : this.od_list){
			get_seeker_possibility(odi);
			get_taker_waiting_possibility(odi);
			get_taker_traveling_possibility(odi);
			get_nomatching_possibility(odi);
			get_every_node_arrival_possibility_for_one_od(odi);
		}
		get_whole_expected_distance();
		get_variables_number();
	}
	
	//得到phaseA被匹配的概率
	public double get_seeker_possibility(OD od){
		List<Node> node_list=od.node_list;
		Node first_node=node_list.get(0);
		double possibility=first_node.possibility;
		od.seeker_probability = possibility;
		return possibility;
	}
	
	//得到phaseB被匹配的概率
	public double get_taker_waiting_possibility(OD od){
		List<Node> node_list=od.node_list;
		Node second_node=node_list.get(1);
		double possibility=second_node.possibility;
		return possibility;
	}
	
	
	public double get_taker_traveling_possibility(OD od){
		double phaseA_possibility=get_seeker_possibility(od);
		double phaseB_possibility=(1-phaseA_possibility)*get_taker_waiting_possibility(od);
		double nomatching_possibility=get_nomatching_possibility(od);
		double phaseC_possibility=1-phaseA_possibility-phaseB_possibility-nomatching_possibility;
		od.taker_traveling_probability = phaseC_possibility;
		od.taker_waiting_probability = phaseB_possibility;
		return phaseC_possibility;
	}
	
	//得到最后未被匹配而离开的概率
	public double get_nomatching_possibility(OD od){
		List<Node> node_list=od.node_list;
		Node last_node=node_list.get(node_list.size()-1);
		double nomatching_possibility=last_node.arrival_rate/od.rate;
		od.whole_matching_probability = 1 - nomatching_possibility;
		return nomatching_possibility;
	}
	
	//得到每个节点的arrival possibility
	public void get_every_node_arrival_possibility_for_one_od(OD od){
		List<Node> node_list = od.node_list;
		double arrival_possibility = 1.0;
		for(Node nodei : node_list){
			nodei.arrival_possiblity = arrival_possibility;
			arrival_possibility = arrival_possibility * (1 - nodei.possibility);
		}
	}
	
	//得到每个OD的 expected_traveling_distance, expected_shared_distance, expected_save_distance
	public void get_node_expected_distance(OD od){
		Node node1_temp = od.node_list.get(0);
		List<Match> matches_temp = node1_temp.matches;
		for(Match match_temp : matches_temp){
			Node node2_temp = match_temp.node2;
			double matching_probability1 = node1_temp.arrival_possiblity * node2_temp.having_possibility * (match_temp.matching_rate/node1_temp.arrival_rate);
			od.expected_traveling_distance = od.expected_traveling_distance + match_temp.distance_node1 * matching_probability1;
			od.expected_shared_distance = od.expected_shared_distance + match_temp.shared_distance * matching_probability1;
			od.expected_save_distance = od.expected_save_distance + match_temp.save_distance * matching_probability1;
			
			OD od2_temp = this.od_list.get(node2_temp.route_type);
			double matching_probability2 = node2_temp.arrival_possiblity * node2_temp.possibility * match_temp.matching_rate/node2_temp.matching_rate;
			od2_temp.expected_traveling_distance = od2_temp.expected_traveling_distance + match_temp.distance_node2 * matching_probability2;
			od2_temp.expected_shared_distance = od2_temp.expected_shared_distance + match_temp.shared_distance * matching_probability2;
			od2_temp.expected_save_distance = od2_temp.expected_save_distance + match_temp.save_distance * matching_probability2;
		}
	}
	
	public void get_whole_expected_distance(){
		for(OD odi : this.od_list){
			get_node_expected_distance(odi);
		}
		for(OD odi : this.od_list){
			odi.expected_traveling_distance = odi.expected_traveling_distance + odi.whole_length * (1 - odi.whole_matching_probability);
		}
	}
	
	//得到总的变量数
	public void get_variables_number(){
		int variables_number = 0;
		for(OD odi : this.od_list){
			for(Node nodej : odi.node_list){
				if(nodej.matches.size() != 0){
					variables_number = variables_number + 6;
				}
			}
		}
		System.out.println(variables_number);
	}
}
