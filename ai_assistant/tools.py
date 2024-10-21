import json
from random import randint
from datetime import date, datetime, time
from llama_index.core.tools import QueryEngineTool, FunctionTool, ToolMetadata
from ai_assistant.rags import TravelGuideRAG
from ai_assistant.prompts import travel_guide_qa_tpl, travel_guide_description
from ai_assistant.config import get_agent_settings
from ai_assistant.models import (
    TripReservation,
    TripType,
    HotelReservation,
    RestaurantReservation,
)
from ai_assistant.utils import save_reservation
import wikipediaapi

SETTINGS = get_agent_settings()

travel_guide_tool = QueryEngineTool(
    query_engine=TravelGuideRAG(
        store_path=SETTINGS.travel_guide_store_path,
        data_dir=SETTINGS.travel_guide_data_path,
        qa_prompt_tpl=travel_guide_qa_tpl,
    ).get_query_engine(),
    metadata=ToolMetadata(
        name="travel_guide", description=travel_guide_description, return_direct=False
    ),
)

def reserve_flight(destination: str, origin: str, date_str: str) -> TripReservation:
    """
    This tool is designed to make flight reservations for users. The tool allows you to reserve a flight by specifying the destination, the origin, and the date of the flight.

    ### Usage
    - Input: The tool requires three inputs:
        1. **destination**: The city to which the user wants to fly.
        2. **origin**: The city from which the flight departs.
        3. **date_str**: The date of the flight in the format 'YYYY-MM-DD'.

    ### Output
    - The tool returns a flight reservation with the following details:
        - Origin and destination cities
        - Flight date
        - Cost

    ### Notes
    - The reservation details are stored.
    - Use this tool when the user asks to book a flight.
    """

    print(
        f"Making flight reservation from {origin} to {destination} on date: {date}"
    )
    reservation = TripReservation(
        trip_type=TripType.flight,
        departure=origin,
        destination=destination,
        date=date.fromisoformat(date_str),
        cost=randint(200, 700),
    )

    save_reservation(reservation)
    return reservation


flight_tool = FunctionTool.from_defaults(fn=reserve_flight, return_direct=False)

def reserve_bus(date_str: str, origin: str, destination: str) -> TripReservation:
    """
    This tool is designed to make bus reservations for users. The tool allows you to book a bus trip by specifying the destination, the departure city, and the date of the trip.

    ### Usage
    - Input: The tool requires three inputs:
        1. **date_str**: The date of the bus trip in the format 'YYYY-MM-DD'.
        2. **origin**: The city from which the bus departs.
        3. **destination**: The city to which the user wants to travel.

    ### Output
    - The tool returns a bus reservation with details such as:
        - Origin and destination cities
        - Trip date
        - Cost

    ### Notes
    - The reservation details are stored.
    - Use this tool when the user asks to book a bus trip.
    """
    print(f"Making bus reservation from {origin} to {destination} on date: {date_str}")
    reservation = TripReservation(
        trip_type=TripType.bus,
        departure=origin,
        destination=destination,
        date=date.fromisoformat(date_str),
        cost=randint(50, 350),
    )

    save_reservation(reservation)
    return reservation

bus_tool = FunctionTool.from_defaults(fn=reserve_bus, return_direct=False)

def reserve_hotel(checkin_str: str, checkout_str: str, hotel_name: str, city: str) -> HotelReservation:
    """
    This tool is designed to make hotel reservations for users. The tool allows you to reserve a hotel stay by specifying the check-in and check-out dates, the hotel name, and the city where the hotel is located.

    ### Usage
    - Input: The tool requires four inputs:
        1. **checkin_str**: The check-in date in the format 'YYYY-MM-DD'.
        2. **checkout_str**: The check-out date in the format 'YYYY-MM-DD'.
        3. **hotel_name**: The name of the hotel where the user wants to stay.
        4. **city**: The city where the hotel is located.

    ### Output
    - The tool returns a hotel reservation with details such as:
        - Check-in and check-out dates
        - Hotel name
        - City of the hotel
        - Cost

    ### Notes
    - The reservation details are stored.
    - Use this tool when the user asks to book a hotel stay.
    """
    print(f"Making hotel reservation at {hotel_name} in {city} from {checkin_str} to {checkout_str}")
    reservation = HotelReservation(
        checkin_date=date.fromisoformat(checkin_str),
        checkout_date=date.fromisoformat(checkout_str),
        hotel_name=hotel_name,
        city=city,
        cost=randint(500, 1000),
    )

    save_reservation(reservation)
    return reservation

hotel_tool = FunctionTool.from_defaults(fn=reserve_hotel, return_direct=False)

def reserve_restaurant(reservation_time_str: str, restaurant: str, city: str, dish: str = "not specified") -> RestaurantReservation:
    """
    This tool is designed to make restaurant reservations for users. The tool allows you to reserve a table at a restaurant by specifying the reservation date and time, the restaurant name, and the city.

    ### Usage
    - Input: The tool requires four inputs:
        1. **reservation_time_str**: The reservation time in the format 'YYYY-MM-DDTHH:MM:SS'.
        2. **restaurant**: The name of the restaurant where the user wants to eat.
        3. **city**: The city where the restaurant is located.
        4. **dish**: (Optional) A specific dish the user would like to order.

    ### Output
    - The tool returns a restaurant reservation with details such as:
        - Reservation time
        - Restaurant name
        - City of the restaurant
        - Cost

    ### Notes
    - The reservation details are stored for future reference.
    - Use this tool when the user asks to book a restaurant reservation.
    """
    reservation_time = datetime.fromisoformat(reservation_time_str)
    print(f"Making restaurant reservation at {restaurant} in {city} at {reservation_time}")
    reservation = RestaurantReservation(
        reservation_time=reservation_time,
        restaurant=restaurant,
        city=city,
        dish=dish,
        cost=randint(100, 500),
    )

    save_reservation(reservation)
    return reservation

restaurant_tool = FunctionTool.from_defaults(fn=reserve_restaurant, return_direct=False)

def trip_summary() -> str:
    """
    This tool generates a summary of the user's trip based on their reservations. It provides a list of reservations by city with their individual costs and also the total cost of the trip.

    ### Usage
    - Input: No input is required from the user.
    - Output: The tool generates a detailed summary including:
        - Activities in each city, along with their dates
        - Total cost of the trip

    ### Notes
    - The tool gets all the trip data from the file trip.json.
    - Use this tool to give users a full overview of their trip plans and costs.
    """
    with open(SETTINGS.log_file, "r") as file:
        trip_data = json.load(file)

    activities_by_city = {}
    total_cost = 0

    for activity in trip_data:
        city = activity.get('city', activity.get('departure', 'unknown'))
        date = activity.get('date', activity.get('checkin_date', activity.get('reservation_time', 'unknown')))
        cost = activity.get('cost', 0)
        total_cost += cost

        if city not in activities_by_city:
            activities_by_city[city] = []

        activities_by_city[city].append({
            'activity': activity.get('reservation_type', 'Actividad'),
            'date': date,
            'details': activity,
        })

    summary = "Trip Summary:\n\n"
    for city, activities in activities_by_city.items():
        summary += f"City: {city}\n"
        for activity in activities:
            summary += f"  - Activity: {activity['activity']}\n"
            summary += f"    Date: {activity['date']}\n"
            summary += f"    Details: {json.dumps(activity['details'], indent=2)}\n"
        summary += "\n"

    summary += f"Total Cost: ${total_cost:.2f}\n"

    return summary

trip_summary_tool = FunctionTool.from_defaults(fn=trip_summary, return_direct=False)

def get_wikipedia_page(lookup_term: str) -> str:
    """
    This tool is designed to retrieve the Wikipedia page for a given term. It allows the user to search for general information about cities, activities, places, and other travel-related topics.

    ### Usage
    - Input: The tool requires one input:
        1. **lookup_term**: The term to search for in Wikipedia (e.g., a city, a place in a city, an event in a city, a holiday in a city, etc.).

    ### Output
    - The tool returns the full text of the Wikipedia page if found. If not, it returns a message saying no page was found.

    ### Notes
    - Use this tool to provide detailed background information or context about places the user is interested in.
    """
    user_agent = 'SegundoParcial/1.0 (https://www.upb.edu/)'
    wiki_wiki = wikipediaapi.Wikipedia(user_agent,'en')
    page = wiki_wiki.page(lookup_term)
    
    if page.exists():
        return page.text
    else:
        return f"No Wikipedia page found for {lookup_term}."

wikipedia_tool = FunctionTool.from_defaults(fn=get_wikipedia_page, return_direct=False)