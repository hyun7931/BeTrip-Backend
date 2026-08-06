import re

import httpx

OG_IMAGE_PATTERN = re.compile(
    r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
# content가 property보다 먼저 오는 경우도 대응
OG_IMAGE_PATTERN_ALT = re.compile(
    r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
    re.IGNORECASE,
)

# <head> 안에서만 찾으면 되므로 응답을 끝까지 받지 않고 앞부분만 읽는다
MAX_BYTES_TO_READ = 65536


def extract_og_image(html: str) -> str | None:
    """HTML 문자열에서 og:image 메타태그 값만 추출하는 순수 함수 (네트워크 I/O 없음)"""
    match = OG_IMAGE_PATTERN.search(html) or OG_IMAGE_PATTERN_ALT.search(html)
    return match.group(1) if match else None


async def fetch_og_image(url: str) -> str | None:
    """
    주어진 URL의 og:image 메타태그 값만 가볍게 읽어온다.
    페이지 전체를 파싱하지 않고, <head>가 포함될 만큼의 앞부분만 스트리밍으로 읽는다.
    실패해도 예외를 던지지 않고 None을 반환한다 (썸네일은 부가 정보이므로).
    """
    try:
        async with httpx.AsyncClient(timeout=3.0, follow_redirects=True) as client:
            async with client.stream("GET", url) as resp:
                if resp.status_code != 200:
                    return None

                chunks = bytearray()
                async for chunk in resp.aiter_bytes():
                    chunks.extend(chunk)
                    if len(chunks) >= MAX_BYTES_TO_READ:
                        break

                html = chunks.decode("utf-8", errors="ignore")
    except httpx.RequestError:
        return None

    return extract_og_image(html)
