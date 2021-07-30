package version2_theory;

public class Match {
	//for simplicity, the type of node1 is point, and the type of node2 is time period by default
	Node node1;
	Node node2;
	double distance_node1;
	double distance_node2;
	double shared_distance;
	double save_distance;
	
	double current_matching_radius;
	double matching_rate;
	
	public Match(Node node1, Node node2, double distance_node1, double distance_node2, double save_distance, double shared_distance){
		this.node1 = node1;
		this.node2 = node2;
		this.distance_node1 = distance_node1;
		this.distance_node2 = distance_node2;
		this.shared_distance = shared_distance;
		this.save_distance = save_distance;
		
		this.matching_rate = 0.0;
		this.current_matching_radius = get_traveling_time(node1.media, node2.media);
	}
	
	public double get_traveling_time(double[] point1,double[] point2){
		return Math.abs(point1[0]-point2[0])+Math.abs(point1[1]-point2[1]);
	}
}
