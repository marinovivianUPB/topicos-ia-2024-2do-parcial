from fastapi import FastAPI, Depends, Query
from llama_index.core.agent import ReActAgent
from ai_assistant.agent import TravelAgent
from ai_assistant.config import get_agent_settings
from ai_assistant.models import AgentAPIResponse, RecommendationRequest, ReservationRequest, HotelReservationRequest,RestaurantReservationRequest
from ai_assistant.tools import (
    reserve_flight,
    reserve_bus,
    reserve_hotel,
    reserve_restaurant
)
import json
from ai_assistant.prompts import agent_prompt_tpl

SETTINGS = get_agent_settings()


def get_agent() -> ReActAgent:
    return TravelAgent(agent_prompt_tpl).get_agent()


app = FastAPI(title="AI Agent")


@app.get("/recommendations/cities")
def recommend_cities(
    notes: list[str] = Query(...), agent: ReActAgent = Depends(get_agent)
):
    prompt = f"Recommend cities in Bolivia to visit with the following notes: {notes}"
    return AgentAPIResponse(status="OK", agent_response=str(agent.chat(prompt)))

@app.get("/recommendations/places")
def recommend_places(
    city: str = Query(...),
    notes: list[str] = Query(None), agent: ReActAgent = Depends(get_agent)
):
    if notes:
        prompt = f"Recommend places to visit in the {city} in Bolivia with the following notes: {notes}"
    else:
        prompt = f"Recommend places to visit in the {city} in Bolivia."
    return AgentAPIResponse(status="OK", agent_response=str(agent.chat(prompt)))

@app.get("/recommendations/hotels")
def recommend_hotels(
    city: str = Query(...),
    notes: list[str] = Query(None), agent: ReActAgent = Depends(get_agent)
):
    if notes:
        prompt = f"Recommend hotels to stay in the {city} in Bolivia with the following notes: {notes}"
    else:
        prompt = f"Recommend hotels to stay in the {city} in Bolivia."
    return AgentAPIResponse(status="OK", agent_response=str(agent.chat(prompt)))

@app.get("/recommendations/activities")
def recommend_activities(
    city: str = Query(...),
    notes: list[str] = Query(None), agent: ReActAgent = Depends(get_agent)
):
    if notes:
        prompt = f"Recommend activities to do in the {city} in Bolivia with the following notes: {notes}"
    else:
        prompt = f"Recommend activities to do in the {city} in Bolivia."
    return AgentAPIResponse(status="OK", agent_response=str(agent.chat(prompt)))


@app.post("/reservations/flight")
def reserve_flight_api(request: RecommendationRequest = Query(...)):
    reservation = reserve_flight(
        request.origin,
        request.destination,
        request.date)
    return AgentAPIResponse(status="OK", agent_response=str(reservation))

@app.post("/reservations/bus")
def reserve_bus_api(request: ReservationRequest = Query(...)):
    reservation = reserve_bus(
        request.date,
        request.origin,
        request.destination)
    return AgentAPIResponse(status="OK", agent_response=str(reservation))

@app.post("/reservations/hotel")
def reserve_hotel_api(request: HotelReservationRequest = Query(...)):
    reservation = reserve_hotel(
        request.checkin_date,
        request.checkout_date,
        request.hotel, request.city)
    return AgentAPIResponse(status="OK", agent_response=str(reservation))

@app.post("/reservations/restaurant")
def reserve_restaurant_api(request: RestaurantReservationRequest = Query(...)):

    if not request.dish:
        request.dish = "not specified"

    reservation = reserve_restaurant(
        f"{request.date}T{request.time}", 
        request.restaurant, 
        request.city, 
        request.dish
    )
    return AgentAPIResponse(status="OK", agent_response=str(reservation))

@app.get("/trip_summary")
def trip_summary(agent: ReActAgent = Depends(get_agent)):

    prompt = f"""
        Please generate a trip summary using the tool `trip_summary_tool`.
        After generating the trip summary, analyze it and generate a detailed report.

        The detailed report should include:
        1. Key highlights of the trip.
        2. Any identified issues or recommendations.
        3. Additional insights based on the generated trip summary.

        Use the `trip_summary_tool` to create the summary as the first step, then follow with the report.

        Please include both the trip summary and the detailed report in **Spanish** in your **final Answer**.
        Make sure to return both the summary and the detailed report as part of the final **Answer**, and not as internal thoughts or reasoning.
        """

    return AgentAPIResponse(
        status="OK",
        agent_response=str(agent.chat(prompt))
    )