package version2_theory;

public class MyThread {
	//parameters
	int[] pick_up_waiting_time = {1, 2, 4, 6, 8, 10};
	int[] maximum_matching_radius = {0, 1, 2, 4, 6, 8, 10};
	int[] maximum_detour_time = {0, 1, 2, 4, 6, 8, 10};
	double[] scales = {1, 0.5, 0.1, 0.06, 0.04, 0.02, 0.01, 0.001};
	
	//input filename
	String od_filename = "D:\\document\\matching probability\\input_data\\version2\\OD.txt";
	
	//output filename
	String filename_base = "D:\\document\\matching probability\\data\\version2\\theory\\";
	
	
	double convergence_tolerance = 0.000001;
	
	public static void main(String args[]){
		MyThread thread = new MyThread();
		
		for(int pi = 0; pi < thread.pick_up_waiting_time.length; pi ++){
			for(int ri = 0; ri < thread.maximum_matching_radius.length; ri ++){
				for(int di = 0; di < thread.maximum_detour_time.length; di ++){
					for(int si = 0; si < thread.scales.length; si ++){
						Senario senario = new Senario(thread.maximum_matching_radius[ri], thread.pick_up_waiting_time[pi], thread.maximum_detour_time[di], thread.scales[si]);
						senario.od_filename = thread.od_filename;
						senario.file_basename = thread.filename_base;
						senario.tolerance = thread.convergence_tolerance;
						String extra_term = pi + "_" + ri + "_" + di + "_" + si + ".txt";
						senario.senario_extra_name = extra_term;
						senario.procedure();
					}
				}
			}
		}
	}
	
	//for test
	public static void main1(String args[]){
		MyThread thread = new MyThread();
		
		for(int pi = 0; pi < 1; pi ++){
			for(int ri = 2; ri < 3; ri ++){
				for(int di = 3; di < 4; di ++){
					for(int si = 2; si < 3; si ++){
						Senario senario = new Senario(thread.maximum_matching_radius[ri], thread.pick_up_waiting_time[pi], thread.maximum_detour_time[di], thread.scales[si]);
						senario.od_filename = thread.od_filename;
						senario.file_basename = thread.filename_base;
						senario.tolerance = thread.convergence_tolerance;
						String extra_term = pi + "_" + ri + "_" + di + "_" + si + ".txt";
						senario.senario_extra_name = extra_term;
						senario.procedure();
					}
				}
			}
		}
	}	
}
