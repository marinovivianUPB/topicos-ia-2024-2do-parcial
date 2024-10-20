import json
from random import randint
from datetime import date, datetime, time
from typing import List
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

def reserve_flight(date_str: str, departure: str, destination: str) -> TripReservation:
    """
    Realiza una reserva de vuelo desde una ciudad de origen hacia un destino en una fecha específica.
    """
    print(
        f"Making flight reservation from {departure} to {destination} on date: {date}"
    )
    reservation = TripReservation(
        trip_type=TripType.flight,
        departure=departure,
        destination=destination,
        date=date.fromisoformat(date_str),
        cost=randint(200, 700),
    )

    save_reservation(reservation)
    return reservation


flight_tool = FunctionTool.from_defaults(fn=reserve_flight, return_direct=False)

def reserve_bus(date_str: str, departure: str, destination: str) -> TripReservation:
    """
    Realiza una reserva de bus desde una ciudad de origen a un destino en una fecha específica.
    """
    print(f"Making bus reservation from {departure} to {destination} on date: {date_str}")
    reservation = TripReservation(
        trip_type=TripType.bus,
        departure=departure,
        destination=destination,
        date=date.fromisoformat(date_str),
        cost=randint(50, 350),
    )

    save_reservation(reservation)
    return reservation

bus_tool = FunctionTool.from_defaults(fn=reserve_bus, return_direct=False)

def reserve_hotel(checkin_str: str, checkout_str: str, hotel_name: str, city: str) -> HotelReservation:
    """
    Realiza una reserva de hotel con nombre del hotel y fechas de check-in y check-out.
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
    Realiza una reserva en un restaurante en una ciudad específica, en una fecha y hora dadas.
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
    user_agent = 'SegundoParcial/1.0 (https://www.upb.edu/)'
    wiki_wiki = wikipediaapi.Wikipedia(user_agent,'en')
    page = wiki_wiki.page(lookup_term)
    
    if page.exists():
        return page.text
    else:
        return f"No Wikipedia page found for {lookup_term}."

wikipedia_tool = FunctionTool.from_defaults(fn=get_wikipedia_page, return_direct=False)