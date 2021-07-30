package version2_simulation;

public class Tool {
	double maximum_matching_radius;
	double maximum_detour_time;
	
	public Tool(double maximum_matching_radius, double maximum_detour_time){
		this.maximum_matching_radius = maximum_matching_radius;
		this.maximum_detour_time = maximum_detour_time;
	}
	
	public double[] get_match_kpi_between_orders(Order order1, Order order2){
		double[] returns = new double[4];
		returns[0] = -1; //distance of order1
		returns[1] = -1; //distance of order2
		returns[2] = -1; //saved distance
		returns[3] = -1; //shared distance
		
		int phase_order1 = order1.phase;
		int phase_order2 = order2.phase;
		if((phase_order1 != 0) && (phase_order2 != 0)){
			return returns;
		}
		
		double[] position_order1 = order1.position.clone();
		double[] position_order2 = order2.position.clone();
		double current_matching_radius = get_traveling_time(position_order1, position_order2);
		if(current_matching_radius > this.maximum_matching_radius){
			return returns;
		}
		
		double min_total_distance = 10000;
		double distance_order1 = 0;
		double distance_order2 = 0;
		double shared_distance = 0;
		boolean flag_matching = false;
		
		double[] start1 = order1.od.origin.clone();
		double[] start2 = order2.od.origin.clone();
		double[] end1 = order1.od.destination.clone();
		double[] end2 = order2.od.destination.clone();
		
		double time_s1_e1 = get_traveling_time(start1,end1);
		double time_s2_e2 = get_traveling_time(start2,end2);
		double time_e1_e2 = get_traveling_time(end1,end2);
		
		if((phase_order1 != 2) && (phase_order2 != 2)){
			//each of the two passengers could be the first one picked up
			double time_s1_s2 = get_traveling_time(start1,start2);			
			double time_s1_e2 = get_traveling_time(start1,end2);			
			double time_s2_e1 = get_traveling_time(start2,end1);
			
			//s1-s2-e1-e2
			double traveling_time1 = time_s1_s2 + time_s2_e1;
			double traveling_time2 = time_s2_e1 + time_e1_e2;
			if(traveling_time1 - time_s1_e1 <= this.maximum_detour_time && traveling_time2 - time_s2_e2 <= this.maximum_detour_time){
				double total_distance = time_s1_s2 + time_s2_e1 + time_e1_e2;
				flag_matching = true;
				if(total_distance < min_total_distance){
					min_total_distance=total_distance;
					distance_order1 = time_s1_s2 + time_s2_e1;
					distance_order2 = time_s2_e1 + time_e1_e2;
					shared_distance = time_s2_e1;
				}
			}
			
			//s1-s2-e2-e1
			traveling_time1 = time_s1_s2 + time_s2_e2 + time_e1_e2;
			if(traveling_time1 - time_s1_e1 <= this.maximum_detour_time){
				double total_distance = time_s1_s2 + time_s2_e2 + time_e1_e2;
				flag_matching=true;
				if(total_distance < min_total_distance){
					min_total_distance = total_distance;
					distance_order1 = time_s1_s2 + time_s2_e2 + time_e1_e2;
					distance_order2 = time_s2_e2;
					shared_distance = time_s2_e2;
				}
			}
			
			//s2-s1-e1-e2
			traveling_time2 = time_s1_s2 + time_s1_e1 + time_e1_e2;
			if(traveling_time2 - time_s2_e2 <= this.maximum_detour_time){
				double total_distance = time_s1_s2 + time_s1_e1 + time_e1_e2;
				flag_matching=true;
				if(total_distance < min_total_distance){
					min_total_distance = total_distance;
					distance_order1 = time_s1_e1;
					distance_order2 = time_s1_s2 + time_s1_e1 + time_e1_e2;
					shared_distance = time_s1_e1;
				}
			}
			
			//s2-s1-e2-e1
			traveling_time1 = time_s1_e2 + time_e1_e2;
			traveling_time2 = time_s1_s2 + time_s1_e2;
			if(traveling_time1 - time_s1_e1 <= this.maximum_detour_time && traveling_time2 - time_s2_e2 <= this.maximum_detour_time){
				double total_distance = time_s1_s2 + time_s1_e2 + time_e1_e2;
				flag_matching = true;
				if(total_distance < min_total_distance){
					min_total_distance = total_distance;
					distance_order1 = time_s1_e2 + time_e1_e2;
					distance_order2 = time_s1_s2 + time_s1_e2;
					shared_distance = time_s1_e2;
				}
			}
			if(flag_matching==true){
				//不仅应该满足上述条件，还应该保证，匹配后的总路径是减少的。但后来仔细想了想，若考虑这种情况，之前的很多东西都需要改，故这个版本暂不考虑这些
				double save_distance = time_s1_e1 + time_s2_e2 - min_total_distance;
				returns[0] = distance_order1;
				returns[1] = distance_order2;
				returns[2] = save_distance;
				returns[3] = shared_distance;
				return returns;
			}else{
				return returns;
			}
		}else if((phase_order1 != 2) && (phase_order2 == 2)){
			double time_s2_w2 = get_traveling_time(start2,position_order2);
			double time_s1_w2 = get_traveling_time(start1,position_order2);
			double time_s1_e2 = get_traveling_time(start1,end2);
			double time_w2_e2 = get_traveling_time(position_order2,end2);
			//w2-s1-e1-e2
			double traveling_time2 = time_s1_w2 + time_s1_e1 + time_e1_e2;
			if(traveling_time2 - time_w2_e2 <= this.maximum_detour_time){
				double total_distance = time_s2_w2 + time_s1_w2 + time_s1_e1 + time_e1_e2;
				flag_matching = true;
				if(total_distance < min_total_distance){
					min_total_distance = total_distance;
					distance_order1 = time_s1_e1;
					distance_order2 = time_s2_w2 + time_s1_w2 + time_s1_e1 + time_e1_e2;
					shared_distance = time_s1_e1;
				}
			}
			//w2-s1-e2-e1
			double traveling_time1 = time_s1_e2 + time_e1_e2;
			traveling_time2 = time_s1_w2 + time_s1_e2;
			if(traveling_time1 - time_s1_e1 <= this.maximum_detour_time && traveling_time2 - time_w2_e2 <= this.maximum_detour_time){
				double total_distance = time_s2_w2 + time_s1_w2 + time_s1_e2 + time_e1_e2;
				flag_matching = true;
				if(total_distance < min_total_distance){
					min_total_distance = total_distance;
					distance_order1 = time_s1_e2 + time_e1_e2;
					distance_order2 = time_s2_w2 + time_s1_w2 + time_s1_e2;
					shared_distance = time_s1_e2;
				}
			}
			if(flag_matching == true){
				//不仅应该满足上述条件，还应该保证，匹配后的总路径是减少的。但后来仔细想了想，若考虑这种情况，之前的很多东西都需要改，故这个版本暂不考虑这些
				double save_distance = time_s1_e1 + time_s2_e2 - min_total_distance;
				returns[0] = distance_order1;
				returns[1] = distance_order2;
				returns[2] = save_distance;
				returns[3] = shared_distance;
				return returns;
				
			}else{
				return returns;
			}
		}else if(phase_order1 == 2 && phase_order2 != 2){
			double time_s1_w1 = get_traveling_time(start1, position_order1);
			double time_w1_s2 = get_traveling_time(position_order1, start2);
			double time_w1_e1 = get_traveling_time(position_order1, end1);
			double time_s2_e1 = get_traveling_time(start2, end1);
			//w1-s2-e1-e2
			double traveling_time1 = time_w1_s2 + time_s2_e1;
			double traveling_time2 = time_s2_e1 + time_e1_e2;
			if(traveling_time1 - time_w1_e1 <= this.maximum_detour_time && traveling_time2 - time_s2_e2 <= this.maximum_detour_time){
				double total_distance = time_s1_w1 + time_w1_s2 + time_s2_e1 + time_e1_e2;
				flag_matching = true;
				if(total_distance < min_total_distance){
					min_total_distance = total_distance;
					distance_order1 = time_s1_w1 + time_w1_s2 + time_s2_e1;
					distance_order2 = time_s2_e1 + time_e1_e2;
					shared_distance = time_s2_e1;
				}
			}
			//w1-s2-e2-e1
			traveling_time1 = time_w1_s2 + time_s2_e2 + time_e1_e2;
			if(traveling_time1 - time_w1_e1 <= this.maximum_detour_time){
				double total_distance = time_s1_w1 + time_w1_s2 + time_s2_e2 + time_e1_e2;
				flag_matching = true;
				if(total_distance < min_total_distance){
					min_total_distance = total_distance;
					distance_order1 = time_s1_w1 + time_w1_s2 + time_s2_e2 + time_e1_e2;
					distance_order2 = time_s2_e2;
					shared_distance = time_s2_e2;
				}
			}
			if(flag_matching == true){
				//不仅应该满足上述条件，还应该保证，匹配后的总路径是减少的。但后来仔细想了想，若考虑这种情况，之前的很多东西都需要改，故这个版本暂不考虑这些
				double save_distance = time_s1_e1 + time_s2_e2 - min_total_distance;
				returns[0] = distance_order1;
				returns[1] = distance_order2;
				returns[2] = save_distance;
				returns[3] = shared_distance;
				return returns;
			}else{
				return returns;
			}
		}
		return returns;
	}
	
	public void update_od_kpi_after_matching_for_two_orders(Order order1, Order order2, double[] returns){
		OD od1 = order1.od;
		OD od2 = order2.od;
		od1.total_traveling_distance = od1.total_traveling_distance + returns[0];
		od1.total_saved_distance = od1.total_saved_distance + returns[2];
		od1.total_shared_distance = od1.total_shared_distance + returns[3];
		od1.total_matched_num = od1.total_matched_num + 1;
		od2.total_traveling_distance = od2.total_traveling_distance + returns[1];
		od2.total_saved_distance = od2.total_saved_distance + returns[2];
		od2.total_shared_distance = od2.total_shared_distance + returns[3];
		od2.total_matched_num = od2.total_matched_num + 1;
	}
	
	public double get_traveling_time(double[] point1,double[] point2){
		return Math.abs(point1[0]-point2[0])+Math.abs(point1[1]-point2[1]);
	}
}
