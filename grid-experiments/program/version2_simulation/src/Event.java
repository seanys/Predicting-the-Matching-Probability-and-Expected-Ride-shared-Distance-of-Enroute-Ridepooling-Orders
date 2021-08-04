package version2_simulation;

public class Event {
	int type; //0: a new order generated; 1: an order picked up by a car; 
			  //2: a car arrive at the destination of the order being served
	double time; // the occurance time of the event considered
	Order order; // corresponding order associated with the event
	OD od; // corresponding od associated with the event
	
	public Event(int type, double time, Order order, OD od){
		this.type = type;
		this.time = time;
		this.order = order;
		this.od = od;
	}
}
