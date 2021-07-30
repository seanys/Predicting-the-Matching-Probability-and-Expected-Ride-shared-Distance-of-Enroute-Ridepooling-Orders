package version2_theory;

import java.util.ArrayList;
import java.util.List;

public class OD {
	double[] origin;
	double[] destination;
	double rate;
	double[][] route;
	double waiting_time;
	List<Node> node_list=new ArrayList<>();
	int OD_index;
	double precision=0.5;//the traveling time on each segment is 0.5 by default
	double whole_length;
	
	double expected_traveling_distance;
	double expected_shared_distance;
	double expected_save_distance;
	
	double seeker_probability;
	double taker_waiting_probability;
	double taker_traveling_probability;
	double whole_matching_probability;
	
	public OD(double waiting_time,double[] origin,double[] destination,double rate,int ODindex){
		this.waiting_time=waiting_time;
		this.origin=origin;
		this.destination=destination;
		this.rate=rate;
		this.OD_index=ODindex;
		
		this.expected_traveling_distance = 0.0;
		this.expected_shared_distance = 0.0;
		this.expected_save_distance = 0.0;
		
		this.seeker_probability = 0.0;
		this.taker_waiting_probability = 0.0;
		this.taker_traveling_probability = 0.0;
		this.whole_matching_probability = 0.0;		
		
		this.route = getRoute_verticle_to_horizontal(origin, destination);
		transferNode();
		
		this.whole_length = get_traveling_time(origin, destination);
	}
	
	public double[][] getRoute_verticle_to_horizontal(double[] origin,double[] destination){
		int routeLength=(int)(Math.abs(origin[0]-destination[0])+Math.abs(origin[1]-destination[1]))*2+1;
		double[][] route=new double[2][routeLength];
		double y_min=Math.min(origin[1], destination[1]);
		double y_max=Math.max(origin[1], destination[1]);
		double x_min=Math.min(origin[0], destination[0]);
		double x_max=Math.max(origin[0], destination[0]);
		int i=0;
		if(origin[1]==y_min){
			for(double y=y_min;y<=y_max;y=y+0.5){
				route[0][i]=origin[0];
				route[1][i]=y;
				i++;
			}
		}else{
			for(double y=y_max;y>=y_min;y=y-0.5){
				route[0][i]=origin[0];
				route[1][i]=y;
				i++;
			}
		}
		if(origin[0]==x_min){
			for(double x=x_min+0.5;x<=x_max;x=x+0.5){
				route[0][i]=x;
				route[1][i]=destination[1];
				i++;
			}
		}else{
			for(double x=x_max-0.5;x>=x_min;x=x-0.5){
				route[0][i]=x;
				route[1][i]=destination[1];
				i++;
			}
		}
		return route;
	}
	
	public double[][] getRoute_horizontal_to_verticle(double[] origin,double[] destination){
		int routeLength=(int)(Math.abs(origin[0]-destination[0])+Math.abs(origin[1]-destination[1]))*2+1;
		double[][] route=new double[2][routeLength];
		double y_min=Math.min(origin[1], destination[1]);
		double y_max=Math.max(origin[1], destination[1]);
		double x_min=Math.min(origin[0], destination[0]);
		double x_max=Math.max(origin[0], destination[0]);
		int i=0;
		if(origin[0]==x_min){
			for(double x=x_min;x<=x_max;x=x+0.5){
				route[0][i]=x;
				route[1][i]=origin[1];
				i++;
			}
		}else{
			for(double x=x_max;x>=x_min;x=x-0.5){
				route[0][i]=x;
				route[1][i]=origin[1];
				i++;
			}
		}
		if(origin[1]==y_min){
			for(double y=y_min+0.5;y<=y_max;y=y+0.5){
				route[0][i]=destination[0];
				route[1][i]=y;
				i++;
			}
		}else{
			for(double y=y_max-0.5;y>=y_min;y=y-0.5){
				route[0][i]=destination[0];
				route[1][i]=y;
				i++;
			}
		}
		
		return route;
	}			
	
	public void transferNode(){		
		Node node0=new Node(0,0,origin,origin,OD_index,0.0,this.origin,this.destination);
		Node node1=new Node(1,1,origin,origin,OD_index,waiting_time,this.origin,this.destination);
		node_list.add(node0);
		node_list.add(node1);

		for(int i=1;i<route[0].length;i++){
			double[] start={route[0][i-1],route[1][i-1]};
			double[] end={route[0][i],route[1][i]};
			Node node_temp0=new Node(1,2,start,end,OD_index,precision,this.origin,this.destination);
			Node node_temp1=new Node(0,2,end,end,OD_index,0.0,this.origin,this.destination);
			node_list.add(node_temp0);
			node_list.add(node_temp1);
		}
	}
	
	public double get_traveling_time(double[] point1,double[] point2){
		return Math.abs(point1[0]-point2[0])+Math.abs(point1[1]-point2[1]);
	}
}
