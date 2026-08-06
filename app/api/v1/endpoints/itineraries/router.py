from app.api.v1.endpoints.itineraries.itineraries import router

# 나중에 장소 담기/제거, 자동생성, 저장 등 새 리소스 파일이 추가되면
# 그때 이 router에 include_router로 합치는 방식으로 바꾸면 됨.
# (지금은 리소스 파일이 itineraries.py 하나뿐이라 그대로 재노출)
__all__ = ["router"]
