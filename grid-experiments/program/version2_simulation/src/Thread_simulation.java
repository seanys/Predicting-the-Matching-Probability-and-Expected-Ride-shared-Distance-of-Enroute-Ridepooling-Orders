package version2_simulation;

import java.util.Date;

public class Thread_simulation {
	public static void main(String args[]){
		Date date1 = new Date();
		double[] pick_up_time_list = {1,2,4,6,8,10};
		double[] maximum_matching_radius_list = {0,1,2,4,6,8,10};
		double[] maximum_detour_time_list = {0,1,2,4,6,8,10};
		double[] scale_list = {1,0.5,0.1,0.06,0.04,0.02,0.01,0.001};
		
		//input filename 
		String od_filename = "D:\\document\\matching probability\\input_data\\version2\\OD.txt";
		
		//output filename
		String od_w_filename_base = "D:\\document\\matching probability\\data\\version2\\simulation\\";
		
		for(int ri = 0; ri < maximum_matching_radius_list.length; ri ++){
		//for(int ri = 2; ri < 3; ri ++){
			MyThread mt = new MyThread(ri);
			mt.od_filename = od_filename;
			mt.od_w_filename_base = od_w_filename_base;
			mt.start();
		}
		Date date2 = new Date();
		System.out.println(date2.getTime() - date1.getTime());
	}
}
