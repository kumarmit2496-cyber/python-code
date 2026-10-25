from fastapi import FastAPI, HTTPException,Query
from courses import courses


app=FastAPI()


@app.get("/welcome")
def get_welcome_msg():
    return {"message": "Welcome to fast Api"}


@app.get("/")
def get_all_courses():
    return courses


@app.get("/course-search")
def search_courses(search: str = Query(..., min_length=1)):
    results = {
        cid: c
        for cid, c in courses.items()
        if search.lower() in c["course_name"].lower()
    }
    if not results:
        raise HTTPException(status_code=404, detail="Course not found")
    return results


@app.get("/courses/{course_id}")
def get_course(course_id: int):
    course = courses.get(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course