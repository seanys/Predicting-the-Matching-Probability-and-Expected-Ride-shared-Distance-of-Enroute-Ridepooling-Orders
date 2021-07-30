package version2_theory;

public class Tools {
	double maximum_matching_radius;
	double maximum_detour_time;
	
	public Tools(double maximum_matching_radius, double maximum_detour_time){
		this.maximum_matching_radius = maximum_matching_radius;
		this.maximum_detour_time = maximum_detour_time;
	}
	
	public double[] get_shared_save_distance(Node node1,Node node2){
		double[] returns = new double[4];
		returns[0] = -1;
		returns[1] = -1;
		returns[2] = -1;
		returns[3] = -1;
		double distance1 = 0.0;
		double distance2 = 0.0;
		double shared_distance = 0.0;
		
		int type1=node1.type;
		int type2=node2.type;
		if(type1==type2){
			return returns;
		}
		int phase1=node1.phase;
		int phase2=node2.phase;
		if(phase1==2 && phase2==2){
			return returns;
		}
		double[] node1_media=node1.media;
		double[] node2_media=node2.media;
		double matching_radius = get_traveling_time(node1_media,node2_media);
		if(matching_radius > this.maximum_matching_radius){
			return returns;
		}
		
		double min_total_distance=10000;
		boolean flag_matching=false;
		
		
		double[] route_end1=node1.route_end;
		double[] route_end2=node2.route_end;
		double[] route_start1=node1.route_start;
		double[] route_start2=node2.route_start;
		double time_s1_e1=get_traveling_time(route_start1,route_end1);
		double time_s2_e2=get_traveling_time(route_start2,route_end2);
		double time_e1_e2=get_traveling_time(route_end1,route_end2);
		//both could be the first one picked up
		if(phase1!=2 && phase2!=2){
			double time_s1_s2=get_traveling_time(route_start1,route_start2);
			double time_s2_e1=get_traveling_time(route_start2,route_end1);
			
			//s1-s2-e1-e2
			double traveling_time1=time_s1_s2+time_s2_e1;
			double traveling_time2=time_s2_e1+time_e1_e2;
			if(traveling_time1-time_s1_e1<=this.maximum_detour_time && traveling_time2-time_s2_e2<=this.maximum_detour_time){
				double total_distance=time_s1_s2+time_s2_e1+time_e1_e2;
				flag_matching=true;
				if(total_distance<min_total_distance){
					shared_distance = time_s2_e1;
					min_total_distance=total_distance;
					distance1 = time_s1_s2 + time_s2_e1;
					distance2 = time_s2_e1 + time_e1_e2;
				}
			}
			
			//s1-s2-e2-e1
			traveling_time1=time_s1_s2+time_s2_e2+time_e1_e2;
			if(traveling_time1-time_s1_e1<=this.maximum_detour_time){
				double total_distance=time_s1_s2+time_s2_e2+time_e1_e2;
				flag_matching=true;
				if(total_distance<min_total_distance){
					shared_distance = time_s2_e2;
					min_total_distance=total_distance;
					distance1 = time_s1_s2 + time_s2_e2 + time_e1_e2;
					distance2 = time_s2_e2;
				}
			}
			
			//s2-s1-e1-e2
			traveling_time2=time_s1_s2+time_s1_e1+time_e1_e2;
			if(traveling_time2-time_s2_e2<=this.maximum_detour_time){
				double total_distance=time_s1_s2+time_s1_e1+time_e1_e2;
				flag_matching=true;
				if(total_distance<min_total_distance){
					shared_distance = time_s1_e1;
					min_total_distance=total_distance;
					distance1 = time_s1_e1;
					distance2 = time_s1_s2 + time_s1_e1 + time_e1_e2;
				}
			}
			
			double time_s1_e2=get_traveling_time(route_start1,route_end2);
			//s2-s1-e2-e1
			traveling_time1=time_s1_e2+time_e1_e2;
			traveling_time2=time_s1_s2+time_s1_e2;
			if(traveling_time1-time_s1_e1<=this.maximum_detour_time && traveling_time2-time_s2_e2<=this.maximum_detour_time){
				double total_distance=time_s1_s2+time_s1_e2+time_e1_e2;
				flag_matching=true;
				if(total_distance<min_total_distance){
					shared_distance = time_s1_e2;
					min_total_distance=total_distance;
					distance1 = time_s1_e2 + time_e1_e2;
					distance2 = time_s1_s2 + time_s1_e2;
				}
			}
			
			if(flag_matching==true){
				double save_distance=time_s1_e1+time_s2_e2-min_total_distance;
				returns[0] = distance1;
				returns[1] = distance2;
				returns[2] = save_distance;
				returns[3] = shared_distance;
				return returns;
			}
			return returns;
		}else if(phase1!=2 && phase2==2){
			double[] position2=new double[2];
			if(node2.type==0){
				position2[0]=node2.media[0];
				position2[1]=node2.media[1];
			}else{
				double[] node_start=node2.start;
				double[] node_end=node2.end;

				double average_traveling_time_on_node=0.25;
				if(node_start[0]==node_end[0]){
					position2[0]=node_start[0];
					if(node_start[1]<node_end[1]){
						position2[1]=node_start[1]+average_traveling_time_on_node;
					}else{
						position2[1]=node_start[1]-average_traveling_time_on_node;
					}
				}else{
					position2[1]=node_start[1];
					if(node_start[0]<node_end[0]){
						position2[0]=node_start[0]+average_traveling_time_on_node;
					}else{
						position2[0]=node_start[0]-average_traveling_time_on_node;
					}
				}
			}
			
			double time_s2_w2=get_traveling_time(route_start2,position2);
			double time_s1_w2=get_traveling_time(position2,route_start1);
			double time_w2_e2=get_traveling_time(position2,route_end2);
			double time_s1_e2=get_traveling_time(route_start1,route_end2);
			//w2-s1-e1-e2
			double traveling_time2=time_s1_w2+time_s1_e1+time_e1_e2;
			if(traveling_time2-time_w2_e2<=this.maximum_detour_time){
				double total_distance=time_s2_w2+time_s1_w2+time_s1_e1+time_e1_e2;
				flag_matching=true;
				if(total_distance<min_total_distance){
					shared_distance = time_s1_e1;
					min_total_distance=total_distance;
					distance1 = time_s1_e1;
					distance2 = time_s2_w2 + time_s1_w2 + time_s1_e1 + time_e1_e2;
				}
			}
			
			//w2-s1-e2-e1
			double traveling_time1=time_s1_e2+time_e1_e2;
			traveling_time2=time_s1_w2+time_s1_e2;
			if(traveling_time1-time_s1_e1<=this.maximum_detour_time && traveling_time2-time_w2_e2<=this.maximum_detour_time){
				double total_distance=time_s2_w2+time_s1_w2+time_s1_e2+time_e1_e2;
				flag_matching=true;
				if(total_distance<min_total_distance){
					shared_distance = time_s1_e2;
					min_total_distance=total_distance;
					distance1 = time_s1_e2 + time_e1_e2;
					distance2 = time_s2_w2 + time_s1_w2 + time_s1_e2;
				}
			}
			if(flag_matching==true){
				double save_distance=time_s1_e1+time_s2_e2-min_total_distance;
				returns[0] = distance1;
				returns[1] = distance2;
				returns[2] = save_distance;
				returns[3] = shared_distance;
				return returns;
			}
			return returns;
		}else if(phase1==2 && phase2!=2){
			double[] position1=new double[2];
			if(node1.type==0){
				position1[0]=node1.media[0];
				position1[1]=node1.media[1];
			}else{
				double[] node_start=node1.start;
				double[] node_end=node1.end;
				double average_traveling_time_on_node=0.25;
				//若横坐标一样，则只需修改纵坐标即可，反之亦然
				if(node_start[0]==node_end[0]){
					position1[0]=node_start[0];
					if(node_start[1]<node_end[1]){
						position1[1]=node_start[1]+average_traveling_time_on_node;
					}else{
						position1[1]=node_start[1]-average_traveling_time_on_node;
					}
				}else{
					position1[1]=node_start[1];
					if(node_start[0]<node_end[0]){
						position1[0]=node_start[0]+average_traveling_time_on_node;
					}else{
						position1[0]=node_start[0]-average_traveling_time_on_node;
					}
				}
			}
			
			double time_s1_w1=get_traveling_time(route_start1,position1);
			double time_w1_s2=get_traveling_time(position1,route_start2);
			double time_s2_e1=get_traveling_time(route_start2,route_end1);
			double time_w1_e1=get_traveling_time(position1,route_end1);
			//w1-s2-e1-e2
			double traveling_time1=time_w1_s2+time_s2_e1;
			double traveling_time2=time_s2_e1+time_e1_e2;
			if(traveling_time1-time_w1_e1<=this.maximum_detour_time && traveling_time2-time_s2_e2<=this.maximum_detour_time){
				double total_distance=time_s1_w1+time_w1_s2+time_s2_e1+time_e1_e2;
				flag_matching=true;
				if(total_distance<min_total_distance){
					shared_distance = time_s2_e1;
					min_total_distance=total_distance;
					distance1 = time_s1_w1 + time_w1_s2 + time_s2_e1;
					distance2 = time_s2_e1 + time_e1_e2;
				}
			}
			
			//w1-s2-e2-e1
			traveling_time1=time_w1_s2+time_s2_e2+time_e1_e2;
			if(traveling_time1-time_w1_e1<=this.maximum_detour_time){
				double total_distance=time_s1_w1+time_w1_s2+time_s2_e2+time_e1_e2;
				flag_matching=true;
				if(total_distance<min_total_distance){
					shared_distance = time_s2_e2;
					min_total_distance=total_distance;
					distance1 = time_s1_w1 + time_w1_s2 + time_s2_e2 + time_e1_e2;
					distance2 = time_s2_e2;
				}
			}
			if(flag_matching==true){
				double save_distance=time_s1_e1+time_s2_e2-min_total_distance;
				returns[0] = distance1;
				returns[1] = distance2;
				returns[2] = save_distance;
				returns[3] = shared_distance;
				return returns;
			}
		}
		return returns;
	}
	
	public double get_traveling_time(double[] point1,double[] point2){
		return Math.abs(point1[0]-point2[0])+Math.abs(point1[1]-point2[1]);
	}
}
