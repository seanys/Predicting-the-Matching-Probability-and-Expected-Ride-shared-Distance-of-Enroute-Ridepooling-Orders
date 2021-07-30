package version2_simulation;

import java.util.Date;

public class MyThread extends Thread{
	double[] pick_up_time_list = {1,2,4,6,8,10};
	double[] maximum_matching_radius_list = {0,1,2,4,6,8,10};
	double[] maximum_detour_time_list = {0,1,2,4,6,8,10};
	double[] scale_list = {1,0.5,0.1,0.06,0.04,0.02,0.01,0.001};
	
	int ri;
	
	//input filename
	String od_filename;
		
	//output_filename
	String od_w_filename_base;
		
	public MyThread(int ri){
		this.ri = ri;
	}
	
	
	
	public void run(){
		for(int pi = 0; pi < this.pick_up_time_list.length; pi ++){
			for(int di = 0; di < this.maximum_detour_time_list.length; di ++){
				for(int si = 0; si < this.scale_list.length; si ++){
		//for(int pi = 0; pi < 1; pi ++){
		//	for(int di = 3; di < 4; di ++){
		//		for(int si = 2; si < 3; si ++){
					
					double start_record_time = 1000/scale_list[si];
					double total_running_time = 4000/scale_list[si];
					
					for(int iteration = 0; iteration < 5; iteration ++){
						Date start_date = new Date();
						Simulation_process sp = new Simulation_process(this.maximum_matching_radius_list[ri], this.pick_up_time_list[pi], this.maximum_detour_time_list[di], this.scale_list[si]);
						sp.od_filename = this.od_filename;
						sp.start_date = start_date;
						String od_w_filename = this.od_w_filename_base + pi + "_" + ri + "_" + di + "_" + si + "_" + iteration + ".txt";
						sp.od_w_filename = od_w_filename;
						sp.start_record_time = start_record_time;
						sp.total_running_time = total_running_time;
						sp.initialize_simulation();
						sp.simulate();
					}
				}
			}
		}
	}
}
