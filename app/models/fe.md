Vok Laagyo FE — Auth / API Mirror Plan
Design-only plan to mirror reg1-dashboard auth and API conventions into the Vok frontend. Do not invent a new architecture; copy-adapt the reference.
[object Object]Constraints

Keep Vok’s existing App Router + features/auth UI; do not redesign login styling.
Match reference conventions as closely as practical.
Prefer small, clear modules over a rewrite.
Adapt response envelope: Vok uses { success, data } (unlike raw user-api { token, user } in places).
[object Object]1. Reference FE auth / API map
Relevant tree
reg1-dashboard/
├── pages/login/index.tsx              # login UI → signIn(...)
├── pages/api/auth/[...nextauth].js    # Credentials → POST {USER_API}/finduser
├── pages/api/user/logout.ts           # BFF logout → user-api
├── pages/_app.tsx                     # SessionProvider
├── components/organisms/AppLayout.tsx # session gate + setToken/setHost
├── utils/axiosConfig.ts               # axios + setToken / setHost
├── utils/api/user.ts                  # browser → /api/user/...
├── utils/hooks/user/useLogout.ts      # logout orchestration
├── types/next-auth.d.ts               # session.jwt, hostName, user fields
└── modules/login/helper.ts            # SSO/tenant flags (skip for Vok v1)
Login end-to-end (credentials)
UI pages/login/index.tsx → signIn('credentials', { email, password, host, redirect: false })
NextAuth POST /api/auth/callback/credentials
Server authorize → POST {NEXT_PUBLIC_USER_API_BASE_URL}/finduser
Body: { email, password }
Header: X-Tenant-Id: <host>
Backend shape (raw): { user, token } (no { success, data } wrapper)
JWT/session callbacks put backend JWT on token.jwt / session.jwt
Storage: NextAuth encrypted JWT cookie (1h). Not localStorage for auth.
AppLayout: if no session → /login?callbackUrl=…; on session → setToken(session.jwt) + setHost(session.hostName)
Product calls: browser → /api/... BFF → microservice with X-Access-Token + X-Tenant-Id from getToken({ req })

Logout: useLogout → logoutUser → POST /api/user/logout → backend /logout with X-Access-Token, then signOut().
Key reference files
[object Object][object Object]2. Target backend (Vok Flask)
Auth routes prefix: /api/v1/users
[object Object]Request: { "email": "...", "password": "..." }
Success: { "success": true, "data": { "token": "<jwt>", "user": { ... } } }
Auth header: X-Access-Token: <jwt>
Dev user: dev@voklaagyo.com / devpassword
[object Object]3. Proposed Vok FE structure
Keep existing UI; add reference-shaped auth/API layers under Vok names (lib/ ≈ utils/, app/api ≈ pages/api).

frontend/src/
├── app/
│   ├── (auth)/login/page.tsx              # KEEP (thin route)
│   ├── layout.tsx                         # wrap SessionProvider
│   ├── api/
│   │   ├── auth/[...nextauth]/route.ts   # NextAuth (credentials only v1)
│   │   └── users/
│   │       ├── logout/route.ts            # BFF → Flask POST /logout
│   │       └── me/route.ts                # BFF → Flask GET /me
│   └── (app)/…                            # protected app routes
├── features/auth/
│   ├── login-page.tsx                     # KEEP UI; wire submit → signIn
│   └── auth-gate.tsx                      # AppLayout-equivalent session gate
├── lib/
│   ├── axios.ts                           # axiosInstance + setToken
│   ├── api/
│   │   └── users.ts                       # logoutUser, getMe → /api/users/...
│   ├── auth/
│   │   ├── options.ts                     # NextAuth options (authorize → finduser)
│   │   └── types.ts                       # next-auth module augmentation
│   └── hooks/auth/
│       ├── useLogout.ts
│       └── useMe.ts                       # optional; RQ over getMe
├── components/providers/
│   └── session-provider.tsx               # next-auth SessionProvider
└── .env.example
    API_URL=http://127.0.0.1:5000          # server-side Flask base
    NEXTAUTH_URL=...
    NEXTAUTH_SECRET=...

Flask targets (server-only from BFF / NextAuth):

POST {API_URL}/api/v1/users/finduser (or /login)
POST {API_URL}/api/v1/users/logout
GET  {API_URL}/api/v1/users/me
[object Object]4. Copy plan (reference → Vok)
[object Object]Envelope unwrap (authorize)
[object Object][object Object]5. Explicit decisions
[object Object][object Object]6. Identical vs rename for Vok
Keep identical

BFF proxy pattern
X-Access-Token header
NextAuth credentials → finduser
Cookie session
setToken on client axios after session
Hooks over raw axios in components
No auth token in localStorage

Adapt / rename

pages/api → app/api/.../route.ts
utils/ → lib/
user domain → users (match Flask /api/v1/users)
Drop X-Tenant-Id / host
Unwrap { success, data }
Keep features/auth UI instead of rebuilding pages/login
[object Object]7. Suggested implementation order
lib/axios.ts + NextAuth options (lib/auth/options.ts) + app/api/auth/[...nextauth]/route.ts
BFF app/api/users/logout + me
Wire login-page.tsx submit → signIn('credentials')
SessionProvider + auth-gate
lib/api/users.ts + useLogout / useMe
[object Object]Status
[x] Structure plan documented
[ ] Implementation (only when explicitly requested)