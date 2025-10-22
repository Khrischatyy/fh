# Implementation TODO List

Track your progress implementing the remaining modules.

## Phase 1: Setup & Testing (30 minutes)

- [ ] Test Docker setup
  ```bash
  cd new_backend
  make dev-build
  ```

- [ ] Run initial migration
  ```bash
  make migrate message="initial migration"
  make upgrade
  ```

- [ ] Test authentication endpoints at http://localhost:8000/docs
  - [ ] Register user
  - [ ] Login
  - [ ] Get current user

- [ ] Verify all services are running
  - [ ] API: http://localhost:8000
  - [ ] PostgreSQL: localhost:5432
  - [ ] Redis: localhost:6379
  - [ ] RabbitMQ: http://localhost:15672

## Phase 2: Simple Modules (2-3 hours)

### Geographic Module
- [ ] Create `src/geographic/schemas.py`
  - [ ] CountryResponse, CountryCreate
  - [ ] CityResponse, CityCreate
- [ ] Create `src/geographic/service.py`
  - [ ] get_countries()
  - [ ] get_country(id)
  - [ ] create_country()
  - [ ] get_cities_by_country()
  - [ ] create_city()
- [ ] Create `src/geographic/router.py`
  - [ ] GET /api/countries
  - [ ] GET /api/countries/{id}
  - [ ] POST /api/countries (admin only)
  - [ ] GET /api/countries/{id}/cities
  - [ ] POST /api/cities (admin only)
- [ ] Register router in main.py
- [ ] Test endpoints
- [ ] Create tests: `tests/geographic/test_service.py`

### Users Module
- [ ] Create `src/users/schemas.py`
  - [ ] UserProfileUpdate
  - [ ] PhotoUploadResponse
  - [ ] SetRoleRequest
- [ ] Create `src/users/service.py`
  - [ ] update_profile()
  - [ ] upload_photo() (S3)
  - [ ] set_role()
  - [ ] get_available_balance()
- [ ] Create `src/users/router.py`
  - [ ] GET /api/user/me
  - [ ] PUT /api/user/update
  - [ ] POST /api/user/upload-photo
  - [ ] POST /api/user/set-role
  - [ ] GET /api/user/available-balance
- [ ] Register router in main.py
- [ ] Test endpoints
- [ ] Create tests: `tests/users/test_service.py`

### Companies Module
- [ ] Create `src/companies/schemas.py`
  - [ ] CompanyCreate, CompanyUpdate, CompanyResponse
  - [ ] AddAdminRequest
- [ ] Create `src/companies/service.py`
  - [ ] create_company()
  - [ ] update_company()
  - [ ] delete_company()
  - [ ] add_admin()
  - [ ] remove_admin()
  - [ ] get_company_by_slug()
- [ ] Create `src/companies/router.py`
  - [ ] POST /api/companies
  - [ ] GET /api/companies/{slug}
  - [ ] PUT /api/companies/{id}
  - [ ] DELETE /api/companies/{id}
  - [ ] POST /api/companies/{id}/admins
  - [ ] DELETE /api/companies/{id}/admins/{user_id}
- [ ] Register router in main.py
- [ ] Test endpoints
- [ ] Create tests: `tests/companies/test_service.py`

## Phase 3: Core Business Modules (4-5 hours)

### Addresses Module (Studios)
- [ ] Create `src/addresses/schemas.py`
  - [ ] AddressCreate, AddressUpdate, AddressResponse
  - [ ] AddressFilter, AddressSearch
  - [ ] OperatingHourCreate, OperatingHourResponse
  - [ ] EquipmentResponse, BadgeResponse
- [ ] Create `src/addresses/service.py`
  - [ ] create_address()
  - [ ] update_address()
  - [ ] delete_address()
  - [ ] get_my_addresses()
  - [ ] get_address_by_slug()
  - [ ] search_addresses()
  - [ ] filter_addresses()
  - [ ] toggle_favorite()
  - [ ] set_operating_hours()
  - [ ] add_equipment()
  - [ ] add_badge()
- [ ] Create `src/addresses/router.py`
  - [ ] POST /api/addresses
  - [ ] GET /api/addresses/my
  - [ ] GET /api/addresses/{slug}
  - [ ] PUT /api/addresses/{id}
  - [ ] DELETE /api/addresses/{id}
  - [ ] POST /api/addresses/search
  - [ ] POST /api/addresses/{id}/favorite
  - [ ] POST /api/addresses/{id}/operating-hours
  - [ ] POST /api/addresses/{id}/equipment
  - [ ] POST /api/addresses/{id}/badges
- [ ] Register router in main.py
- [ ] Test endpoints
- [ ] Create tests: `tests/addresses/test_service.py`

### Rooms Module
- [ ] Create `src/rooms/schemas.py`
  - [ ] RoomCreate, RoomUpdate, RoomResponse
  - [ ] RoomPhotoCreate, RoomPhotoResponse
  - [ ] RoomPriceCreate, RoomPriceResponse
- [ ] Create `src/rooms/service.py`
  - [ ] create_room()
  - [ ] update_room()
  - [ ] delete_room()
  - [ ] upload_photo()
  - [ ] reorder_photos()
  - [ ] delete_photo()
  - [ ] set_prices()
  - [ ] get_room_prices()
- [ ] Create `src/rooms/router.py`
  - [ ] POST /api/rooms
  - [ ] PUT /api/rooms/{id}
  - [ ] DELETE /api/rooms/{id}
  - [ ] POST /api/rooms/{id}/photos
  - [ ] PUT /api/rooms/{id}/photos/order
  - [ ] DELETE /api/photos/{id}
  - [ ] POST /api/rooms/{id}/prices
  - [ ] GET /api/rooms/{id}/prices
- [ ] Create `src/rooms/utils.py` for S3 upload
- [ ] Register router in main.py
- [ ] Test endpoints
- [ ] Create tests: `tests/rooms/test_service.py`

## Phase 4: Complex Features (6-8 hours)

### Bookings Module
- [ ] Create `src/bookings/schemas.py`
  - [ ] BookingCreate, BookingResponse
  - [ ] AvailabilityRequest, AvailabilityResponse
  - [ ] PriceCalculationRequest, PriceCalculationResponse
  - [ ] BookingFilter
- [ ] Create `src/bookings/service.py`
  - [ ] check_availability()
  - [ ] get_available_times()
  - [ ] calculate_price()
  - [ ] create_booking()
  - [ ] confirm_booking()
  - [ ] cancel_booking()
  - [ ] get_my_bookings()
  - [ ] get_booking_history()
  - [ ] filter_bookings()
  - [ ] expire_temporary_links() (background task)
- [ ] Create `src/bookings/router.py`
  - [ ] POST /api/bookings/check-availability
  - [ ] GET /api/bookings/available-times
  - [ ] POST /api/bookings/calculate-price
  - [ ] POST /api/bookings
  - [ ] POST /api/bookings/{id}/confirm
  - [ ] POST /api/bookings/{id}/cancel
  - [ ] GET /api/bookings/my
  - [ ] GET /api/bookings/history
  - [ ] POST /api/bookings/filter
- [ ] Create `src/tasks/booking.py` for expiry task
- [ ] Register router in main.py
- [ ] Test booking flow
- [ ] Create tests: `tests/bookings/test_service.py`

### Payments Module
- [ ] Create `src/payments/schemas.py`
  - [ ] StripeAccountCreate, StripeAccountResponse
  - [ ] SquareAuthResponse
  - [ ] PaymentSessionCreate, PaymentSessionResponse
  - [ ] PayoutCreate, PayoutResponse
  - [ ] RefundRequest
- [ ] Create `src/payments/services/stripe_service.py`
  - [ ] create_account()
  - [ ] get_account_link()
  - [ ] create_payment_session()
  - [ ] verify_payment()
  - [ ] process_refund()
  - [ ] get_balance()
  - [ ] create_payout()
- [ ] Create `src/payments/services/square_service.py`
  - [ ] oauth_redirect()
  - [ ] oauth_callback()
  - [ ] create_payment_session()
  - [ ] verify_payment()
  - [ ] process_refund()
  - [ ] get_balance()
  - [ ] create_payout()
- [ ] Create `src/payments/service.py` (gateway abstraction)
  - [ ] get_gateway_service()
  - [ ] create_payment_session()
  - [ ] verify_payment()
  - [ ] process_refund()
- [ ] Create `src/payments/router.py`
  - [ ] POST /api/payments/stripe/account
  - [ ] GET /api/payments/stripe/account-link
  - [ ] GET /api/payments/stripe/balance
  - [ ] GET /api/payments/square/oauth
  - [ ] GET /api/payments/square/callback
  - [ ] POST /api/payments/session
  - [ ] POST /api/payments/verify
  - [ ] POST /api/payments/refund
  - [ ] POST /api/payouts
  - [ ] GET /api/payouts
- [ ] Register router in main.py
- [ ] Test payment flows
- [ ] Create tests: `tests/payments/test_service.py`

### Messages Module
- [ ] Create `src/messages/schemas.py`
  - [ ] MessageCreate, MessageResponse
  - [ ] ChatListResponse
  - [ ] MessageHistoryResponse
- [ ] Create `src/messages/service.py`
  - [ ] send_message()
  - [ ] get_messages()
  - [ ] get_chat_list()
  - [ ] mark_as_read()
  - [ ] get_unread_count()
- [ ] Create `src/messages/router.py`
  - [ ] POST /api/messages
  - [ ] GET /api/messages/chats
  - [ ] GET /api/messages/history
  - [ ] POST /api/messages/{id}/read
  - [ ] GET /api/messages/unread-count
- [ ] Register router in main.py
- [ ] Test messaging
- [ ] Create tests: `tests/messages/test_service.py`

### Teams Module
- [ ] Create `src/teams/schemas.py`
  - [ ] TeamMemberCreate, TeamMemberResponse
  - [ ] InvitationCreate, InvitationResponse
- [ ] Create `src/teams/service.py`
  - [ ] invite_member()
  - [ ] add_member()
  - [ ] remove_member()
  - [ ] get_team_members()
  - [ ] check_email()
- [ ] Create `src/teams/router.py`
  - [ ] POST /api/teams/members
  - [ ] GET /api/teams/members
  - [ ] DELETE /api/teams/members/{id}
  - [ ] POST /api/teams/invite
  - [ ] GET /api/teams/check-email
- [ ] Register router in main.py
- [ ] Test team management
- [ ] Create tests: `tests/teams/test_service.py`

## Phase 5: Additional Features (5-10 hours)

### Authentication Enhancements
- [ ] Implement email verification tokens (Redis)
- [ ] Implement password reset tokens (Redis)
- [ ] Add token cleanup/expiry

### File Uploads
- [ ] Complete S3 upload utility
- [ ] Add image validation
- [ ] Add image resizing (Pillow)
- [ ] Add file size limits

### Performance & Features
- [ ] Add pagination helper
- [ ] Add rate limiting (SlowAPI)
- [ ] Add caching layer (Redis)
- [ ] Add search indexing

### Webhooks
- [ ] Stripe webhook handler
- [ ] Square webhook handler
- [ ] Payment verification

### Background Jobs
- [ ] Booking expiry cron job
- [ ] Payment reminder emails
- [ ] Payout processing

### Production Setup
- [ ] Create nginx.conf for production
- [ ] Add SSL/TLS configuration
- [ ] Set up monitoring (Sentry)
- [ ] Add health check endpoints
- [ ] Configure log rotation

## Phase 6: Testing & Documentation (3-5 hours)

### Testing
- [ ] Write integration tests
- [ ] Test complete user flows
- [ ] Test error scenarios
- [ ] Load testing
- [ ] Security testing

### Documentation
- [ ] Add API examples to README
- [ ] Create Postman collection
- [ ] Document environment setup
- [ ] Add troubleshooting guide
- [ ] Create deployment guide

### Code Quality
- [ ] Run full linting
- [ ] Achieve 80%+ test coverage
- [ ] Code review
- [ ] Performance optimization

## Deployment Checklist

- [ ] Update .env with production values
- [ ] Generate secure SECRET_KEY
- [ ] Configure production database
- [ ] Set up S3 bucket
- [ ] Configure email service
- [ ] Set up payment gateways (live mode)
- [ ] Configure domain and SSL
- [ ] Set up monitoring
- [ ] Create database backups
- [ ] Deploy with `make prod`
- [ ] Run smoke tests
- [ ] Monitor logs

## Notes

- Check off items as you complete them
- Refer to IMPLEMENTATION_GUIDE.md for code templates
- Use auth module as reference for patterns
- Test each module before moving to the next
- Commit frequently with clear messages

---

**Current Status**: Foundation complete ✅
**Next Step**: Start with Geographic module (easiest)
**Estimated Time**: 15-20 hours for all modules
