package version2_theory;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileWriter;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

public class IO {
	double pick_up_waiting_time;
	double scale;
	List<OD> od_list;
	
	boolean flag_termination;
	long running_time;
	int iteration_number;
	
	
	//input filenames
	String od_filename;
	
	//output filenames
	String filename_one_senario_result;
	
	public IO(double pick_up_waiting_time, double scale){
		this.pick_up_waiting_time = pick_up_waiting_time;
		this.scale = scale;
		
		od_list = new ArrayList<>();
	}
	
	public IO(boolean flag_termination, long running_time, int iteration_number, List<OD> od_list){
		this.flag_termination = flag_termination;
		this.running_time = running_time;
		this.iteration_number = iteration_number;
		this.od_list = od_list;
	}
	
	
	public void readOD(){
		try{
			InputStreamReader isr=new InputStreamReader(new FileInputStream(new File(this.od_filename)));
			BufferedReader br=new BufferedReader(isr);
			//instantiate an OD pair after reading every line
			String line;
			int index=0;
			while((line=br.readLine())!=null){
				String[] line_array=line.split("\t");
				double ox=Double.parseDouble(line_array[0]);
				double oy=Double.parseDouble(line_array[1]);
				double dx=Double.parseDouble(line_array[2]);
				double dy=Double.parseDouble(line_array[3]);
				double route_length = Double.parseDouble(line_array[4]);
				double rate=Double.parseDouble(line_array[5]);
				double type = Double.parseDouble(line_array[6]);
				double[] origin={ox,oy};
				double[] destination={dx,dy};
				if(type != 2.0){
					od_list.add(new OD(this.pick_up_waiting_time,origin,destination,rate*this.scale,index));
					index++;
				}
				
			}
			br.close();
		}catch(Exception e){
			e.printStackTrace();
		}
	}
	
	public void write_one_senario(){
		try{
			BufferedWriter bw=new BufferedWriter(new FileWriter(this.filename_one_senario_result,true));
			bw.write(String.valueOf(this.flag_termination) + "\t" + this.running_time + "\t" + this.iteration_number + "\r\n");
			bw.write("seeker\ttaker_waiting\ttaker_traveling\twhole_probability\texpected_traveling_distance\texpected_shared_distance\texpected_save_distance\r\n");
			for(OD odi : this.od_list){
				bw.write(odi.seeker_probability + "\t" + odi.taker_waiting_probability + "\t" + odi.taker_traveling_probability + "\t"
						+ odi.whole_matching_probability + "\t" + odi.expected_traveling_distance + "\t"
						+ odi.expected_shared_distance + "\t" + odi.expected_save_distance + "\r\n");
			}
			bw.close();
		}catch(Exception e){
			e.printStackTrace();
		}
	}
}
