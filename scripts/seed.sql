-- 로컬 개발/Swagger 수동 테스트용 시드 데이터.

-- 실행: psql -U postgres -d betrip -f scripts/seed.sql
-- (DATABASE_URL은 .env 참고. 이미 존재하는 행은 건드리지 않음 — 여러 번 실행해도 안전)

-- 로그인 정보: seed@example.com / Passw0rd!
-- POST /api/v1/auth/login 으로 로그인 후 access_token을 Swagger Authorize에 넣고 테스트할 것.

-- 1. 테스트 유저
INSERT INTO users (user_id, email, password_hash, nickname, provider)
VALUES (
    '11111111-1111-1111-1111-111111111111',
    'seed@example.com',
    '$2b$12$kesxl6h/bg0mofh02ZBYtuQDVoZDsW5SDtlUO7p.60fhyootgCr4W',
    '시드유저',
    'LOCAL'
)
ON CONFLICT (email) DO NOTHING;

-- 2. 테스트 일정 2건 (목록/상세 확인용)
INSERT INTO itineraries (
    itinerary_id, user_id, title, status, region,
    start_date, end_date, arrival_time, departure_time,
    transportation, purpose, styles
)
VALUES
    (
        '22222222-2222-2222-2222-222222222222',
        '11111111-1111-1111-1111-111111111111',
        '제주도 3박4일', 'DRAFT', '제주도',
        '2026-08-10', '2026-08-13', 'LUNCH', 'MORNING',
        'CAR', 'FAMILY', '["NATURE", "FOOD"]'
    ),
    (
        '33333333-3333-3333-3333-333333333333',
        '11111111-1111-1111-1111-111111111111',
        '전주 당일치기', 'SAVED', '전주',
        '2026-09-01', '2026-09-01', 'MORNING', 'EVENING',
        'PUBLIC_TRANSPORT', 'FRIEND', '["FOOD"]'
    ),
    (
        '55555555-5555-5555-5555-555555555555',
        '11111111-1111-1111-1111-111111111111',
        '부산 이동수단/목적 미정', 'DRAFT', '부산',
        '2026-10-05', '2026-10-07', 'LUNCH', 'EVENING',
        NULL, NULL, '[]'
    )
ON CONFLICT (itinerary_id) DO NOTHING;

-- 3. 테스트 장소 2건 + 담긴 장소 1건
--    kakao-12345/kakao-67890 두 곳은 검색(GET /map/search) 없이도 바로
--    GET /map/transit?from=kakao-12345&to=kakao-67890&mode=CAR(또는 WALK) 테스트가 가능하도록 실좌표로 넣어둠
--    (GET /map/places/{place_id}는 kakao-12345로, GET /map/search는 실제 카카오 API를 호출하니 시드 불필요)
INSERT INTO places (place_id, name, category, address, lat, lng, place_url)
VALUES
    (
        'kakao-12345', '협재해수욕장', 'ACTIVITY', '제주시 한림읍',
        33.3938, 126.2397, 'https://place.map.kakao.com/12345'
    ),
    (
        'kakao-67890', '제주국제공항', 'ACTIVITY', '제주시 용담2동',
        33.5066, 126.4930, 'https://place.map.kakao.com/67890'
    )
ON CONFLICT (place_id) DO NOTHING;

INSERT INTO itinerary_places (itinerary_place_id, itinerary_id, place_id, day, time_slot, order_in_day)
VALUES (
    '44444444-4444-4444-4444-444444444444',
    '22222222-2222-2222-2222-222222222222',
    'kakao-12345', 1, 'LUNCH', 1
)
ON CONFLICT (itinerary_id, place_id) DO NOTHING;
