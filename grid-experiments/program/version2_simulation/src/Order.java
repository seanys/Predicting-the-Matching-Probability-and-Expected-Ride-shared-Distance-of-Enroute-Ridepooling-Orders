package version2_simulation;

public class Order {
	double[] position;
	int phase; //0: seeker; 1: taker waiting in their origin;
				//2: taker traveling along the route
	OD od;
	double start_time;
	int status; // 0: unmatched; 1: matched
	
	double waiting_time;
	
	public Order(double[] position, int phase, OD od, double start_time, int status, double waiting_time){
		this.position = position.clone();
		this.phase = phase;
		this.od = od;
		this.start_time = start_time;
		this.status = 0;
		this.waiting_time = waiting_time;
	}
	
	public void set_position(double current_time){
		double traveling_time = current_time - this.start_time;
		if(traveling_time <= this.waiting_time){
			return;
		}
		traveling_time = traveling_time - waiting_time;
		
		//assume driver travel following vertical direction first then horizontally 
		double[] start_point = this.od.origin.clone();
		double[] end_point = this.od.destination.clone();
		double y_min = Math.min(start_point[1], end_point[1]);
		double vertical_traveling_time = Math.abs(start_point[1] - end_point[1]);
		
		if(y_min == start_point[1]){
			if(traveling_time <= vertical_traveling_time){
				this.position[0] = start_point[0];
				this.position[1] = y_min + traveling_time;
			}else{
				this.position[1] = end_point[1];
				if(start_point[0] < end_point[0]){
					this.position[0] = start_point[0] + traveling_time - vertical_traveling_time;
				}else{
					this.position[0] = start_point[0] - (traveling_time - vertical_traveling_time);
				}
			}
		}else{
			if(traveling_time <= vertical_traveling_time){
				this.position[0] = start_point[0];
				this.position[1] = start_point[1] - traveling_time;
			}else{
				this.position[1] = end_point[1];
				if(start_point[0] <= end_point[0]){
					this.position[0] = start_point[0] + traveling_time - vertical_traveling_time;
				}else{
					this.position[0] = start_point[0] - (traveling_time - vertical_traveling_time);
				}
			}
		}
	}
}
