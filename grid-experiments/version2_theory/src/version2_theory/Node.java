package version2_theory;

import java.util.ArrayList;
import java.util.List;

public class Node {
	int phase; //0: seeker status; 1: taker waiting at the origin; 2: taker traveling along the route
	double[] start; //start point, end point and median point 's coordination
	double[] end;
	double[] media;
	int type; //0: time point; 1: time period
	double arrival_rate; //the arrival rate of the node
	double matching_rate; //applied only when its type is 1
	double having_possibility; //the probability of there being available passenger in the node
	int route_type; //the OD pair which the node belongs to
	double possibility; //the matching probability of passengers who arrive at the node
	double arrival_possiblity; //the probability of passenger arriving at the node
	double time; //the time duration in the node
	double[] route_start;
	double[] route_end;
	double current_pick_up_time;//temporary variable, applied only when determining the priority of matching nodes
	
	List<Match> matches;
	
	public Node(int type,int phase,double[] start,double[] end,int route_type,double time,double[] route_start,double[] route_end){
		this.type=type;
		this.phase=phase;
		this.start=start;
		this.end=end;
		this.media=new double[2];
		this.media[0]=(this.start[0]+this.end[0])/2;
		this.media[1]=(this.start[1]+this.end[1])/2;
		this.route_type=route_type;
		this.time=time;
		this.matching_rate=0;
		this.having_possibility=0;
		this.possibility=0;
		this.route_start=route_start;
		this.route_end=route_end;
		this.arrival_rate=0;
		this.arrival_possiblity = 0.0;
		
		this.matches = new ArrayList<>();
	}
}
