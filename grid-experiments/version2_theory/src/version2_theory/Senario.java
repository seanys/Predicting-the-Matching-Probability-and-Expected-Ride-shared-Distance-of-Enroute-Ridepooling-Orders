package version2_theory;

import java.util.List;


public class Senario {
	double maximum_matching_radius;
	double pick_up_waiting_time;
	double maximum_detour_time;
	double scale;
	
	List<OD> od_list;
	
	//the following parameter need to specified when make up an instance
	//input filename
	String od_filename;
	
	//output filename
	String file_basename;
	String senario_extra_name;
	
	//parameters
	double tolerance;
	
	
	public Senario(double maximum_matching_radius, double pick_up_waiting_time, double maximum_detour_time, double scale){
		this.maximum_matching_radius = maximum_matching_radius;
		this.pick_up_waiting_time = pick_up_waiting_time;
		this.maximum_detour_time = maximum_detour_time;
		this.scale = scale;
	}
	
	
	public void initialize(){
		IO read_io = new IO(this.pick_up_waiting_time, this.scale);
		read_io.od_filename = od_filename;
		read_io.readOD();
		this.od_list = read_io.od_list;
		OD_relation od_relation = new OD_relation(this.maximum_matching_radius, this.pick_up_waiting_time, this.maximum_detour_time, this.od_list);
	}
	
	public void result_handle(boolean flag_termination, long running_time, int iteration_number){
		IO output_io = new IO(flag_termination, running_time, iteration_number, this.od_list);
		output_io.filename_one_senario_result = this.file_basename + this.senario_extra_name;
		output_io.write_one_senario();
	}
	
	public void procedure(){
		initialize();
		Process process = new Process(this.od_list, this.tolerance);
		process.iteration();
		Result_handle result_handle_class = new Result_handle(this.od_list);
		result_handle(process.flag_termination, process.running_duration, process.iteration_number);
	}
}
