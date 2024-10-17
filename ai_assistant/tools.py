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


# Tool functions
def reserve_flight(date_str: str, departure: str, destination: str) -> TripReservation:
    """
    ===> COMPLETE DESCRIPTION HERE <===
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
