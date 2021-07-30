package version2_simulation;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileWriter;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

public class IO {
	double scale;
	List<OD> od_list;
	
	//input filenames
	String od_filename;
	
	//output filename
	String od_w_filename;
	
	public IO(double scale){
		this.scale = scale;
		
		od_list = new ArrayList<>();
	}
	
	public void readOD(){
		try{
			InputStreamReader isr=new InputStreamReader(new FileInputStream(new File(this.od_filename)));
			BufferedReader br=new BufferedReader(isr);
			//initialize an od instance for each line
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
					od_list.add(new OD(origin,destination,rate*this.scale));
				}
				
			}
			br.close();
		}catch(Exception e){
			e.printStackTrace();
		}
	}
	
	public void write_OD(long running_time){
		try{
			BufferedWriter bw = new BufferedWriter(new FileWriter(this.od_w_filename, true));
			bw.write(running_time + "\r\n");
			for(OD odi : this.od_list){
				bw.write(odi.total_num + "\t" + odi.seeker_num + "\t" + odi.taker_waiting_num + "\t"
						+ odi.taker_traveling_num + "\t" + odi.leave_num + "\t" + odi.total_matched_num + "\t"
						+ odi.total_traveling_distance + "\t" + odi.total_shared_distance + "\t"
						+ odi.total_saved_distance + "\r\n");
			}
			bw.close();
		}catch(Exception e){
			e.printStackTrace();
		}
	}
}
