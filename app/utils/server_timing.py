def format_server_timing(timings: dict[str, float]) -> str:
    """
    (개발용)
    dict를 표준 HTTP `Server-Timing` 헤더 값으로 변환한다.
    이 헤더가 응답에 실려 있으면 Chrome 개발자도구에서
    Network 탭 > 요청 클릭 > Timing 패널에 항목별 소요시간이 막대그래프로 자동 표시된다.
    """
    return ", ".join(f"{name};dur={duration:.1f}" for name, duration in timings.items())
