# SomRoyal School EMS — Portal Brand Identity & Color Palette Documentation

> **Status:** Verified Live via Browser DevTools & Source Code Inspection  
> **Target Portal:** `http://127.0.0.1:5173/admin/dashboard`  
> **Inspection Mode:** Non-destructive Computed CSS Extraction & AST Verification  
> **Date:** November 12, 2026  

---

## 1. Executive Brand Identity Overview

SomRoyal School EMS (Hawlwadaag Secondary School) is an enterprise academic management platform designed around a **Modern Academic & Enterprise SaaS** visual language.

The portal's visual architecture is constructed on:
- **Primary Brand Base:** Deep Midnight Navy (`#0A192F` and `#1E3A8A`) providing institutional authority, structure, and enterprise contrast.
- **Vibrant Interactive Accents:** High-energy Solar Orange (`#FF5722` to `#FF6B35`) used for active navigation pills, brand initials badges, and critical action buttons, paired with Vivid Royal Blue (`#2563EB`) and Amber (`#D97706`).
- **Surface Elevation System:** Crisp Pure White (`#FFFFFF`) layered over Ultra-light Slate canvas (`#F8FAFC`), supported by subtle border scaffolding (`#E2E8F0` and `#CBD5E1`).
- **Harmonized Metric Tints:** Soft pastel gradients for statistics and operational KPIs (Emerald `#ECFDF5`, Amber `#FFFBEB`, Lavender `#FAF5FF`, Coral `#FEF2F2`, Ice Blue `#EEF5FE`).

---

## 2. Complete Color Usage Directory

Every color discovered in the live application and source code is documented below with its exact UI location, computed RGB values, and design function.

| No. | Component | UI Location | Color Purpose | HEX Code | RGB |
|---|---|---|---|---|---|
| 1 | Global Canvas | Document `<body>` | App background canvas | `#F8FAFC` | `rgb(248, 250, 252)` |
| 2 | Sidebar | Main aside container (`.admin-sidebar`) | Main sidebar background | `#0A192F` | `rgb(10, 25, 47)` |
| 3 | Sidebar | School header container (`.sidebar-header`) | Top school branding header | `#081528` | `rgb(8, 21, 40)` |
| 4 | Sidebar | Active navigation item (`.nav-item.active`) | Active link gradient start | `#FF6B35` | `rgb(255, 107, 53)` |
| 5 | Sidebar | Active navigation item (`.nav-item.active`) | Active link gradient end | `#FF5722` | `rgb(255, 87, 34)` |
| 6 | Sidebar | Active navigation text & icon | Active link text & icon | `#FFFFFF` | `rgb(255, 255, 255)` |
| 7 | Sidebar | Active navigation glow shadow | Active link elevation shadow | `rgba(255, 87, 34, 0.40)` | `rgba(255, 87, 34, 0.4)` |
| 8 | Sidebar | Inactive navigation link text | Inactive link text & icon | `#94A3B8` | `rgb(148, 163, 184)` |
| 9 | Sidebar | Navigation link hover state | Link hover background | `rgba(255, 255, 255, 0.05)` | `rgba(255, 255, 255, 0.05)` |
| 10 | Sidebar | Navigation link hover text | Link hover text color | `#F8FAFC` | `rgb(248, 250, 252)` |
| 11 | Sidebar | School initials avatar badge | Badge gradient start | `#FF6500` | `rgb(255, 101, 0)` |
| 12 | Sidebar | School initials avatar badge | Badge gradient end | `#FF8A00` | `rgb(255, 138, 0)` |
| 13 | Sidebar | Navigation chevron icon | Navigation disclosure indicator | `#64748B` | `rgb(100, 116, 139)` |
| 14 | Sidebar | Support help card background | Dark glass support card | `rgba(15, 23, 42, 0.65)` | `rgba(15, 23, 42, 0.65)` |
| 15 | Sidebar | Support help card border | Translucent white card border | `rgba(255, 255, 255, 0.08)` | `rgba(255, 255, 255, 0.08)` |
| 16 | Sidebar | Support help icon circle | Support icon container | `rgba(37, 99, 235, 0.15)` | `rgba(37, 99, 235, 0.15)` |
| 17 | Sidebar | Support help icon color | Sky blue support icon | `#38BDF8` | `rgb(56, 189, 248)` |
| 18 | Sidebar | Right vertical border divider | Boundary between sidebar & content | `rgba(255, 255, 255, 0.06)` | `rgba(255, 255, 255, 0.06)` |
| 19 | Sidebar | Mobile drawer backdrop overlay | Modal screen dimming | `rgba(15, 23, 42, 0.70)` | `rgba(15, 23, 42, 0.7)` |
| 20 | Header | Top navbar container (`.admin-header`) | Fixed header surface | `#FFFFFF` | `rgb(255, 255, 255)` |
| 21 | Header | Bottom divider border | Bottom header boundary | `#E2E8F0` | `rgb(226, 232, 240)` |
| 22 | Header | Search container background | Search bar input surface | `#F8FAFC` | `rgb(248, 250, 252)` |
| 23 | Header | Search container border | Inactive search border | `#E2E8F0` | `rgb(226, 232, 240)` |
| 24 | Header | Search input focus border | Focused search state | `#3B82F6` | `rgb(59, 130, 246)` |
| 25 | Header | Search input focus ring glow | Focus halo | `rgba(59, 130, 246, 0.12)` | `rgba(59, 130, 246, 0.12)` |
| 26 | Header | Search text color | User input text | `#1E293B` | `rgb(30, 41, 59)` |
| 27 | Header | Search placeholder & icon | Inactive search cue | `#94A3B8` | `rgb(148, 163, 184)` |
| 28 | Header | Shortcut pill (`Ctrl + K`) | Keyboard shortcut badge | `#FFFFFF` | `rgb(255, 255, 255)` |
| 29 | Header | Shortcut pill border | Shortcut keycap border | `#CBD5E1` | `rgb(203, 213, 225)` |
| 30 | Header | Notification button background | Notification bell trigger surface | `#F8FAFC` | `rgb(248, 250, 252)` |
| 31 | Header | Notification button border | Bell trigger border | `#E2E8F0` | `rgb(226, 232, 240)` |
| 32 | Header | Notification button icon | Bell SVG icon | `#475569` | `rgb(71, 85, 105)` |
| 33 | Header | Notification badge background | Unread alert badge | `#EF4444` | `rgb(239, 68, 68)` |
| 34 | Header | Notification badge text | Unread counter number | `#FFFFFF` | `rgb(255, 255, 255)` |
| 35 | Header | Notification badge shadow | Unread alert glow | `rgba(239, 68, 68, 0.40)` | `rgba(239, 68, 68, 0.4)` |
| 36 | Header | User avatar background | Admin initials circle | `#1E293B` | `rgb(30, 41, 59)` |
| 37 | Header | User avatar text | Initials letter | `#FFFFFF` | `rgb(255, 255, 255)` |
| 38 | Header | Admin display name | Primary user name text | `#0F172A` | `rgb(15, 23, 42)` |
| 39 | Header | Admin role subtitle | User role label | `#64748B` | `rgb(100, 116, 139)` |
| 40 | Header | Notification unread item card | Highlighted unread alert card | `#F0F7FF` | `rgb(240, 247, 255)` |
| 41 | Header | Notification unread item hover | Highlighted unread hover state | `#E6F0FD` | `rgb(230, 240, 253)` |
| 42 | Header | Notification unread indicator dot | Glowing blue unread pip | `#2563EB` | `rgb(37, 99, 235)` |
| 43 | Header | Language dropdown trigger pill | Language selector background | `#F8FAFC` | `rgb(248, 250, 252)` |
| 44 | Header | Language dropdown active option | Selected language highlight | `#EFF6FF` | `rgb(239, 246, 255)` |
| 45 | Header | User dropdown logout text & icon | Dangerous action indicator | `#EF4444` | `rgb(239, 68, 68)` |
| 46 | Header | User dropdown logout hover | Dangerous hover highlight | `#FEF2F2` | `rgb(254, 242, 242)` |
| 47 | Dashboard | Hero banner gradient start | Deep midnight gradient base | `#071E46` | `rgb(7, 30, 70)` |
| 48 | Dashboard | Hero banner gradient mid | Rich royal blue midpoint | `#0D47A1` | `rgb(13, 71, 161)` |
| 49 | Dashboard | Hero banner gradient end | Vivid sky blue accent endpoint | `#0284C7` | `rgb(2, 132, 199)` |
| 50 | Dashboard | Hero card shadow | Banner drop elevation | `rgba(7, 30, 70, 0.35)` | `rgba(7, 30, 70, 0.35)` |
| 51 | Dashboard | Hero heading text | Welcome greeting | `rgba(255, 255, 255, 0.90)`| `rgba(255, 255, 255, 0.9)` |
| 52 | Dashboard | Hero subtitle text | Welcome descriptor | `rgba(255, 255, 255, 0.85)`| `rgba(255, 255, 255, 0.85)` |
| 53 | Dashboard | Hero academic year select | Translucent dropdown surface | `rgba(255, 255, 255, 0.15)`| `rgba(255, 255, 255, 0.15)` |
| 54 | Dashboard | Hero academic year border | Glass selector outline | `rgba(255, 255, 255, 0.25)`| `rgba(255, 255, 255, 0.25)` |
| 55 | Stat Cards | Total Students card background start | Soft ice blue gradient start | `#EEF5FE` | `rgb(238, 245, 254)` |
| 56 | Stat Cards | Total Students card background end | Soft ice blue gradient end | `#E0EEFF` | `rgb(224, 238, 255)` |
| 57 | Stat Cards | Total Students card border | Ice blue border outline | `#BFDBFE` | `rgb(191, 219, 254)` |
| 58 | Stat Cards | Total Students icon gradient | Royal blue icon badge start | `#2563EB` | `rgb(37, 99, 235)` |
| 59 | Stat Cards | Total Students icon gradient end | Royal blue icon badge end | `#1D4ED8` | `rgb(29, 78, 216)` |
| 60 | Stat Cards | Total Teachers card background start | Soft mint green start | `#EDFCF7` | `rgb(237, 252, 247)` |
| 61 | Stat Cards | Total Teachers card background end | Soft mint green end | `#D4F7EA` | `rgb(212, 247, 234)` |
| 62 | Stat Cards | Total Teachers card border | Mint green border outline | `#A7F3D0` | `rgb(167, 243, 208)` |
| 63 | Stat Cards | Total Teachers icon gradient start | Emerald green icon badge start | `#10B981` | `rgb(16, 185, 129)` |
| 64 | Stat Cards | Total Teachers icon gradient end | Emerald green icon badge end | `#059669` | `rgb(5, 150, 105)` |
| 65 | Stat Cards | Total Classes card background start | Soft lavender start | `#F7F3FE` | `rgb(247, 243, 254)` |
| 66 | Stat Cards | Total Classes card background end | Soft lavender end | `#E9E0FD` | `rgb(233, 224, 253)` |
| 67 | Stat Cards | Total Classes card border | Lavender border outline | `#DDD6FE` | `rgb(221, 214, 254)` |
| 68 | Stat Cards | Total Classes icon gradient start | Violet icon badge start | `#8B5CF6` | `rgb(139, 92, 246)` |
| 69 | Stat Cards | Total Classes icon gradient end | Violet icon badge end | `#7C3AED` | `rgb(124, 58, 237)` |
| 70 | Stat Cards | Total Subjects card background start | Soft peach start | `#FEF7EE` | `rgb(254, 247, 238)` |
| 71 | Stat Cards | Total Subjects card background end | Soft peach end | `#FDE7CC` | `rgb(253, 231, 204)` |
| 72 | Stat Cards | Total Subjects card border | Peach border outline | `#FED7AA` | `rgb(254, 215, 170)` |
| 73 | Stat Cards | Total Subjects icon gradient start | Warm orange icon badge start | `#F97316` | `rgb(249, 115, 22)` |
| 74 | Stat Cards | Total Subjects icon gradient end | Warm orange icon badge end | `#EA580C` | `rgb(234, 88, 12)` |
| 75 | Stat Cards | Today's Classes card background start | Soft amber start | `#FFFBEB` | `rgb(255, 251, 235)` |
| 76 | Stat Cards | Today's Classes card background end | Soft amber end | `#FEF3C7` | `rgb(254, 243, 199)` |
| 77 | Stat Cards | Today's Classes card border | Amber border outline | `#FDE68A` | `rgb(253, 230, 138)` |
| 78 | Stat Cards | Today's Classes icon gradient start | Amber icon badge start | `#F59E0B` | `rgb(245, 158, 11)` |
| 79 | Stat Cards | Today's Classes icon gradient end | Amber icon badge end | `#D97706` | `rgb(217, 119, 6)` |
| 80 | Stat Cards | Upcoming Exams card background start | Soft rose coral start | `#FEF2F2` | `rgb(254, 242, 242)` |
| 81 | Stat Cards | Upcoming Exams card background end | Soft rose coral end | `#FEE2E2` | `rgb(254, 226, 226)` |
| 82 | Stat Cards | Upcoming Exams card border | Rose border outline | `#FECACA` | `rgb(254, 202, 202)` |
| 83 | Stat Cards | Upcoming Exams icon gradient start | Coral red icon badge start | `#EF4444` | `rgb(239, 68, 68)` |
| 84 | Stat Cards | Upcoming Exams icon gradient end | Coral red icon badge end | `#DC2626` | `rgb(220, 38, 38)` |
| 85 | Stat Cards | Fees Collected card background start | Soft emerald tint start | `#ECFDF5` | `rgb(236, 253, 245)` |
| 86 | Stat Cards | Fees Collected card background end | Soft emerald tint end | `#D1FAE5` | `rgb(209, 250, 229)` |
| 87 | Stat Cards | Fees Collected card border | Emerald border outline | `#A7F3D0` | `rgb(167, 243, 208)` |
| 88 | Stat Cards | Outstanding Fees card background start| Soft royal purple start | `#FAF5FF` | `rgb(250, 245, 255)` |
| 89 | Stat Cards | Outstanding Fees card background end | Soft royal purple end | `#EDE9FE` | `rgb(237, 233, 254)` |
| 90 | Stat Cards | Outstanding Fees card border | Violet purple border outline | `#DDD6FE` | `rgb(221, 214, 254)` |
| 91 | Stat Cards | KPI Card metric label text | Card header descriptor | `#334155` | `rgb(51, 65, 85)` |
| 92 | Stat Cards | KPI Card metric numerical value | Primary numerical data | `#0F172A` | `rgb(15, 23, 42)` |
| 93 | Stat Cards | Positive trend pill background | Growth trend container | `#DCFCE7` | `rgb(220, 252, 231)` |
| 94 | Stat Cards | Positive trend pill text | Growth percentage text | `#15803D` | `rgb(21, 128, 61)` |
| 95 | Action Tiles | `Register New Student` button | Quick action tile text & icon | `#2563EB` | `rgb(37, 99, 235)` |
| 96 | Action Tiles | `Register New Student` border | Quick action tile outline | `#BFDBFE` | `rgb(191, 219, 254)` |
| 97 | Action Tiles | `Add Teacher` button | Quick action tile text & icon | `#059669` | `rgb(5, 150, 105)` |
| 98 | Action Tiles | `Add Teacher` border | Quick action tile outline | `#A7F3D0` | `rgb(167, 243, 208)` |
| 99 | Action Tiles | `Create Class` button | Quick action tile text & icon | `#7C3AED` | `rgb(124, 58, 237)` |
| 100 | Action Tiles | `Create Class` border | Quick action tile outline | `#DDD6FE` | `rgb(221, 214, 254)` |
| 101 | Action Tiles | `Generate Timetable` button | Quick action tile text & icon | `#EA580C` | `rgb(234, 88, 12)` |
| 102 | Action Tiles | `Generate Timetable` border | Quick action tile outline | `#FED7AA` | `rgb(254, 215, 170)` |
| 103 | Action Tiles | Quick action button background | Tile container surface | `#FFFFFF` | `rgb(255, 255, 255)` |
| 104 | Tables | Table container card | Data grid wrapper surface | `#FFFFFF` | `rgb(255, 255, 255)` |
| 105 | Tables | Table column headers (`<th>`) | Uppercase column descriptor | `#475569` | `rgb(71, 85, 105)` |
| 106 | Tables | Table row horizontal separator | Inter-row divider border | `#F1F5F9` | `rgb(241, 245, 249)` |
| 107 | Tables | Table row hover background | Cursor focus highlight | `#F8FAFC` | `rgb(248, 250, 252)` |
| 108 | Tables | Table cell primary text (`<td>`) | Normal table content | `#1E293B` | `rgb(30, 41, 59)` |
| 109 | Tables | Table filter dropdown background | Select input surface | `#F8FAFC` | `rgb(248, 250, 252)` |
| 110 | Tables | Table filter dropdown border | Select input boundary | `#E2E8F0` | `rgb(226, 232, 240)` |
| 111 | Tables | Table filter dropdown text | Select option label | `#334155` | `rgb(51, 65, 85)` |
| 112 | Tables | Table pagination container | Bottom pagination bar surface| `#F8FAFC` | `rgb(248, 250, 252)` |
| 113 | Tables | Table pagination top border | Pagination boundary divider | `#E2E8F0` | `rgb(226, 232, 240)` |
| 114 | Buttons | Primary button background (`.btn-primary`) | Solid primary call to action | `#1E3A8A` | `rgb(30, 58, 138)` |
| 115 | Buttons | Primary button hover state | Primary button hover highlight| `#1E40AF` | `rgb(30, 64, 175)` |
| 116 | Buttons | Primary button text | Button label text | `#FFFFFF` | `rgb(255, 255, 255)` |
| 117 | Buttons | Secondary button background (`.btn-secondary`)| Alternate action background | `#F1F5F9` | `rgb(241, 245, 249)` |
| 118 | Buttons | Secondary button hover | Alternate action hover | `#E2E8F0` | `rgb(226, 232, 240)` |
| 119 | Buttons | Secondary button border | Alternate action outline | `#CBD5E1` | `rgb(203, 213, 225)` |
| 120 | Buttons | Secondary button text | Alternate action label | `#0F172A` | `rgb(15, 23, 42)` |
| 121 | Buttons | Outline button text & border (`.btn-outline`) | Transparent framed action | `#1E3A8A` | `rgb(30, 58, 138)` |
| 122 | Buttons | Outline button hover background | Frame hover tint | `#EFF6FF` | `rgb(239, 246, 255)` |
| 123 | Buttons | Danger button background (`.btn-danger`) | Destructive action background | `#EF4444` | `rgb(239, 68, 68)` |
| 124 | Buttons | Danger button hover background | Destructive action hover | `#DC2626` | `rgb(220, 38, 38)` |
| 125 | Forms | Input label text (`.form-label`) | Form field identifier | `#0F172A` | `rgb(15, 23, 42)` |
| 126 | Forms | Form input field background (`.form-control`) | Data entry surface | `#FFFFFF` | `rgb(255, 255, 255)` |
| 127 | Forms | Form input default border | Field boundary line | `#CBD5E1` | `rgb(203, 213, 225)` |
| 128 | Forms | Form input focus border | Active entry highlight | `#3B82F6` | `rgb(59, 130, 246)` |
| 129 | Forms | Form input focus ring halo | Accessible focus indicator | `rgba(59, 130, 246, 0.15)` | `rgba(59, 130, 246, 0.15)` |
| 130 | Forms | Form input disabled background | Non-editable input state | `#F1F5F9` | `rgb(241, 245, 249)` |
| 131 | Forms | Form input error border (`.has-error`) | Validation failure outline | `#EF4444` | `rgb(239, 68, 68)` |
| 132 | Forms | Form input error text (`.error-msg`) | Validation message text | `#EF4444` | `rgb(239, 68, 68)` |
| 133 | Forms | Password toggle button icon | Reveal password icon | `#64748B` | `rgb(100, 116, 139)` |
| 134 | Badges | Success badge background (`.badge-success`)| Passed / Completed state bg | `#ECFDF5` | `rgb(236, 253, 245)` |
| 135 | Badges | Success badge border | Passed / Completed outline | `#A7F3D0` | `rgb(167, 243, 208)` |
| 136 | Badges | Success badge text & dot | Passed / Completed text | `#065F46` | `rgb(6, 95, 70)` |
| 137 | Badges | Warning badge background (`.badge-warning`)| Pending / In-progress bg | `#FFFBEB` | `rgb(255, 251, 235)` |
| 138 | Badges | Warning badge border | Pending / In-progress border | `#FDE68A` | `rgb(253, 230, 138)` |
| 139 | Badges | Warning badge text & dot | Pending / In-progress text | `#92400E` | `rgb(146, 64, 14)` |
| 140 | Badges | Danger badge background (`.badge-danger`) | Failed / Inactive status bg | `#FEF2F2` | `rgb(254, 242, 242)` |
| 141 | Badges | Danger badge border | Failed / Inactive status outline | `#FECACA` | `rgb(254, 202, 202)` |
| 142 | Badges | Danger badge text & dot | Failed / Inactive status text | `#991B1B` | `rgb(153, 27, 27)` |
| 143 | Badges | Info badge background (`.badge-info`) | General notice status bg | `#EFF6FF` | `rgb(239, 246, 255)` |
| 144 | Badges | Info badge border | General notice status outline| `#BFDBFE` | `rgb(191, 219, 254)` |
| 145 | Badges | Info badge text & dot | General notice status text | `#1E40AF` | `rgb(30, 64, 175)` |
| 146 | Badges | Neutral badge background (`.badge-neutral`)| Draft / Archive status bg | `#F1F5F9` | `rgb(241, 245, 249)` |
| 147 | Badges | Neutral badge border | Draft / Archive status outline| `#E2E8F0` | `rgb(226, 232, 240)` |
| 148 | Badges | Neutral badge text | Draft / Archive status text | `#64748B` | `rgb(100, 116, 139)` |
| 149 | Modals | Dialog modal surface (`.modal-container`) | Dialog elevated surface | `#FFFFFF` | `rgb(255, 255, 255)` |
| 150 | Modals | Dialog header bottom divider | Header divider border | `#F1F5F9` | `rgb(241, 245, 249)` |
| 151 | Modals | Dialog backdrop shadow overlay | Dimming backdrop screen | `rgba(15, 23, 42, 0.60)` | `rgba(15, 23, 42, 0.6)` |

---

## 3. Visual Color Palette Swatches

### 3.1 Primary Brand Colors
- `[ #0A192F ]` **Deep Midnight Navy** (`rgb(10, 25, 47)`) — Found in: Sidebar root container (`.admin-sidebar`). Purpose: Brand anchor & institutional foundation.
- `[ #1E3A8A ]` **Classic Oxford Navy** (`rgb(30, 58, 138)`) — Found in: Primary action buttons (`.btn-primary`). Purpose: Authoritative brand action color.
- `[ #1E40AF ]` **Dark Oxford Blue** (`rgb(30, 64, 175)`) — Found in: Primary button hover states & info badge text. Purpose: Hover depth.
- `[ #EFF6FF ]` **Subtle Brand Tint** (`rgb(239, 246, 255)`) — Found in: Button outlines, dropdown highlights. Purpose: Soft background highlight.

### 3.2 Secondary & Accent Brand Colors
- `[ #0284C7 ]` **Vivid Sky Blue** (`rgb(2, 132, 199)`) — Found in: Hero banner gradient termination stop. Purpose: Modern vibrancy.
- `[ #FF5722 ]` **Deep Solar Orange** (`rgb(255, 87, 34)`) — Found in: Active sidebar navigation pill & support CTA. Purpose: Vibrant interactive focus.
- `[ #FF6B35 ]` **Vibrant Tangerine Orange** (`rgb(255, 107, 53)`) — Found in: Active sidebar navigation gradient start. Purpose: Warmth and visual warmth.
- `[ #D97706 ]` **Warm Amber Accent** (`rgb(217, 119, 6)`) — Found in: Operational attendance KPI icons & warning accents. Purpose: Secondary warm accent.

### 3.3 Sidebar Colors
- `[ #0A192F ]` **Sidebar Canvas** (`rgb(10, 25, 47)`) — Main background.
- `[ #081528 ]` **Sidebar Header** (`rgb(8, 21, 40)`) — Top school branding header.
- `[ #FF6B35 ]` & `[ #FF5722 ]` **Active Nav Pill Gradient** — Active page indicator.
- `[ #94A3B8 ]` **Inactive Nav Text & Icon** (`rgb(148, 163, 184)`) — Default link typography.
- `[ #F8FAFC ]` **Hover Nav Text** (`rgb(248, 250, 252)`) — Focused link typography.
- `[ rgba(255,255,255,0.05) ]` **Nav Hover Surface** — Subtle frosted white hover backdrop.
- `[ rgba(255,255,255,0.06) ]` **Sidebar Separator Border** — Structural dividers.
- `[ #38BDF8 ]` **Support Help Icon** (`rgb(56, 189, 248)`) — Light sky blue support beacon.

### 3.4 Header / Top Navigation Colors
- `[ #FFFFFF ]` **Navbar Canvas** (`rgb(255, 255, 255)`) — Fixed pure white surface.
- `[ #E2E8F0 ]` **Navbar Divider Border** (`rgb(226, 232, 240)`) — Subtle bottom divider.
- `[ #F8FAFC ]` **Search Container Surface** (`rgb(248, 250, 252)`) — Inset input well.
- `[ #3B82F6 ]` **Search Active Ring** (`rgb(59, 130, 246)`) — Accessible focus ring.
- `[ #EF4444 ]` **Notification Badge** (`rgb(239, 68, 68)`) — Unread counter badge.
- `[ #1E293B ]` **User Avatar Circle** (`rgb(30, 41, 59)`) — Dark slate avatar badge.
- `[ #F0F7FF ]` **Unread Notification Card** (`rgb(240, 247, 255)`) — Unread row highlight.

### 3.5 Dashboard Colors & Hero Canvas
- `[ #071E46 ]` **Hero Gradient Start (Midnight)** (`rgb(7, 30, 70)`) — Deep navy start.
- `[ #0D47A1 ]` **Hero Gradient Mid (Royal Blue)** (`rgb(13, 71, 161)`) — Vibrant blue midpoint.
- `[ #0284C7 ]` **Hero Gradient End (Sky Blue)** (`rgb(2, 132, 199)`) — Sky blue accent.
- `[ rgba(255,255,255,0.15) ]` **Hero Glass Select** — Translucent academic year dropdown.
- `[ rgba(255,255,255,0.25) ]` **Hero Glass Outline** — Glass border.

### 3.6 Card Colors (Stat Cards & Panels)
- `[ #EEF5FE ]` -> `[ #E0EEFF ]` **Ice Blue Gradient** (Border: `#BFDBFE`) — Total Students Card.
- `[ #EDFCF7 ]` -> `[ #D4F7EA ]` **Mint Green Gradient** (Border: `#A7F3D0`) — Total Teachers Card.
- `[ #F7F3FE ]` -> `[ #E9E0FD ]` **Lavender Gradient** (Border: `#DDD6FE`) — Total Classes Card.
- `[ #FEF7EE ]` -> `[ #FDE7CC ]` **Peach Gradient** (Border: `#FED7AA`) — Total Subjects Card.
- `[ #FFFBEB ]` -> `[ #FEF3C7 ]` **Amber Gradient** (Border: `#FDE68A`) — Today's Classes Card.
- `[ #FEF2F2 ]` -> `[ #FEE2E2 ]` **Rose Coral Gradient** (Border: `#FECACA`) — Upcoming Exams Card.
- `[ #ECFDF5 ]` -> `[ #D1FAE5 ]` **Emerald Gradient** (Border: `#A7F3D0`) — Fees Collected Card.
- `[ #FAF5FF ]` -> `[ #EDE9FE ]` **Violet Purple Gradient** (Border: `#DDD6FE`) — Outstanding Fees Card.

### 3.7 Table Colors
- `[ #FFFFFF ]` **Table Surface** (`rgb(255, 255, 255)`) — Grid background.
- `[ #475569 ]` **Column Header Text** (`rgb(71, 85, 105)`) — Table headers (`<th>`).
- `[ #F1F5F9 ]` **Row Separator Border** (`rgb(241, 245, 249)`) — Row borders (`<tr>`).
- `[ #F8FAFC ]` **Row Hover State** (`rgb(248, 250, 252)`) — Interactive row hover.
- `[ #1E293B ]` **Primary Cell Content** (`rgb(30, 41, 59)`) — Cell text (`<td>`).
- `[ #F8FAFC ]` **Pagination Bar Surface** (`rgb(248, 250, 252)`) — Table footer.

### 3.8 Button Colors
- `[ #1E3A8A ]` **Primary Button Base** (`rgb(30, 58, 138)`) — Standard primary CTA.
- `[ #1E40AF ]` **Primary Button Hover** (`rgb(30, 64, 175)`) — Primary hover state.
- `[ #F1F5F9 ]` **Secondary Button Base** (`rgb(241, 245, 249)`) — Subtle alternate button.
- `[ #E2E8F0 ]` **Secondary Button Hover** (`rgb(226, 232, 240)`) — Subtle hover state.
- `[ #EF4444 ]` **Danger Button Base** (`rgb(239, 68, 68)`) — Destructive action.
- `[ #DC2626 ]` **Danger Button Hover** (`rgb(220, 38, 38)`) — Destructive hover state.

### 3.9 Typography Hierarchy Colors
- `[ #0F172A ]` **Heading / Heavy Dark** (`rgb(15, 23, 42)`) — Page titles, KPI numbers, labels.
- `[ #1E293B ]` **Body Slate** (`rgb(30, 41, 59)`) — Standard body text and table cells.
- `[ #475569 ]` **Secondary Body** (`rgb(71, 85, 105)`) — Column headers, notification bodies.
- `[ #64748B ]` **Muted / Subtitle** (`rgb(100, 116, 139)`) — Role subtitles, chevrons, timestamps.
- `[ #94A3B8 ]` **Light Tertiary / Placeholder** (`rgb(148, 163, 184)`) — Search placeholders, inactive icons.
- `[ #FFFFFF ]` **Inverse White** (`rgb(255, 255, 255)`) — Dark background text & active labels.

### 3.10 Border Colors
- `[ #E2E8F0 ]` **Subtle Border** (`rgb(226, 232, 240)`) — Main divider, card border, header bottom.
- `[ #CBD5E1 ]` **Medium Border** (`rgb(203, 213, 225)`) — Form input boundary, secondary button border.
- `[ #3B82F6 ]` **Focus Border** (`rgb(59, 130, 246)`) — Input active focus outline.
- `[ #F1F5F9 ]` **Hairline Table Border** (`rgb(241, 245, 249)`) — Subtle table row border.
- `[ rgba(255,255,255,0.06) ]` **Dark Surface Border** — Translucent sidebar dividers.

### 3.11 Semantic Status Colors
- **Success (Green):**
  - Indicator: `#10B981` (`rgb(16, 185, 129)`)
  - Background Tint: `#ECFDF5` (`rgb(236, 253, 245)`)
  - Outline Border: `#A7F3D0` (`rgb(167, 243, 208)`)
  - Deep Text: `#065F46` (`rgb(6, 95, 70)`)
- **Warning (Amber):**
  - Indicator: `#F59E0B` (`rgb(245, 158, 11)`)
  - Background Tint: `#FFFBEB` (`rgb(255, 251, 235)`)
  - Outline Border: `#FDE68A` (`rgb(253, 230, 138)`)
  - Deep Text: `#92400E` (`rgb(146, 64, 14)`)
- **Danger (Red):**
  - Indicator: `#EF4444` (`rgb(239, 68, 68)`)
  - Background Tint: `#FEF2F2` (`rgb(254, 242, 242)`)
  - Outline Border: `#FECACA` (`rgb(254, 202, 202)`)
  - Deep Text: `#991B1B` (`rgb(153, 27, 27)`)
- **Info (Blue):**
  - Indicator: `#3B82F6` (`rgb(59, 130, 246)`)
  - Background Tint: `#EFF6FF` (`rgb(239, 246, 255)`)
  - Outline Border: `#BFDBFE` (`rgb(191, 219, 254)`)
  - Deep Text: `#1E40AF` (`rgb(30, 64, 175)`)

---

## 4. Shared & Repeated Color Analysis (Duplicate Cross-References)

The following master colors are systematically reused across multiple distinct components:

| HEX Code | RGB Value | Reused UI Locations | Component Roles |
|---|---|---|---|
| `#F8FAFC` | `rgb(248, 250, 252)` | 1. Global `<body>`<br>2. Header search input well<br>3. Notification trigger button<br>4. Table row hover state<br>5. Table pagination footer<br>6. Language dropdown pill | Universal light background canvas & input well |
| `#FFFFFF` | `rgb(255, 255, 255)` | 1. Header surface (`.admin-header`)<br>2. Form inputs (`.form-control`)<br>3. Quick action tile surfaces<br>4. Table card container<br>5. Modal containers<br>6. Active navigation text | Pure surface canvas & high-contrast text |
| `#0F172A` | `rgb(15, 23, 42)` | 1. Page title typography<br>2. Stat card numerical values<br>3. Form input labels (`.form-label`)<br>4. Admin user full name in header | High-contrast structural typography |
| `#E2E8F0` | `rgb(226, 232, 240)` | 1. Header bottom border<br>2. Search container border<br>3. Table filter border<br>4. Table pagination top border<br>5. Card default border (`var(--border-subtle)`) | Primary subtle structural border divider |
| `#CBD5E1` | `rgb(203, 213, 225)` | 1. Shortcut keycap pill border<br>2. Secondary button border<br>3. Form input default border (`var(--border-medium)`) | Medium-weight boundary border |
| `#EF4444` | `rgb(239, 68, 68)` | 1. Header notification badge<br>2. Upcoming exams stat card icon<br>3. Form input validation error border & text<br>4. Danger button (`.btn-danger`)<br>5. User dropdown logout button | Universal danger & attention alert indicator |
| `#2563EB` | `rgb(37, 99, 235)` | 1. Total Students stat icon gradient<br>2. Notification unread pip & "Mark all read"<br>3. `Register New Student` quick action tile<br>4. Header user role badge text | Interactive primary blue accent |
| `#94A3B8` | `rgb(148, 163, 184)` | 1. Sidebar inactive navigation text & icon<br>2. Header search icon & placeholder<br>3. Notification timestamp text<br>4. Inactive form hint text | Tertiary placeholder & inactive iconography |

---

## 5. Source Code References

Each color is traced directly to its authoritative source file, CSS variable, or scoped style rule:

| Color Role | HEX Code | Source File Path | CSS Variable / Class Name |
|---|---|---|---|
| Main App Canvas | `#F8FAFC` | `frontend/src/assets/styles/main.css` | `--bg-app` |
| Surface Canvas | `#FFFFFF` | `frontend/src/assets/styles/main.css` | `--bg-surface` |
| Primary Brand Navy | `#1E3A8A` | `frontend/src/assets/styles/main.css` | `--brand-primary` / `.btn-primary` |
| Primary Hover Navy | `#1E40AF` | `frontend/src/assets/styles/main.css` | `--brand-primary-hover` |
| Primary Light Tint | `#EFF6FF` | `frontend/src/assets/styles/main.css` | `--brand-primary-light` |
| Secondary Sky Blue | `#0284C7` | `frontend/src/assets/styles/main.css` | `--brand-secondary` |
| Amber Brand Accent | `#D97706` | `frontend/src/assets/styles/main.css` | `--brand-accent` |
| Sidebar Canvas | `#0A192F` | `frontend/src/components/admin/AdminSidebar.vue` | `.admin-sidebar` (line 307) |
| Sidebar Header | `#081528` | `frontend/src/components/admin/AdminSidebar.vue` | `.sidebar-header` (line 306) |
| Active Nav Pill | `#FF6B35` / `#FF5722` | `frontend/src/components/admin/AdminSidebar.vue` | `.nav-item.active` (line 442) |
| Inactive Nav Item | `#94A3B8` | `frontend/src/components/admin/AdminSidebar.vue` | `.nav-item` (line 428) |
| Header Canvas | `#FFFFFF` | `frontend/src/components/admin/AdminHeader.vue` | `.admin-header` (line 569) |
| Header Divider | `#E2E8F0` | `frontend/src/components/admin/AdminHeader.vue` | `.admin-header` (line 570) |
| Search Well | `#F8FAFC` | `frontend/src/components/admin/AdminHeader.vue` | `.search-container` (line 618) |
| Notification Badge | `#EF4444` | `frontend/src/components/admin/AdminHeader.vue` | `.notification-badge` (line 840) |
| Hero Banner Gradient | `#071E46` -> `#0284C7` | `frontend/src/views/admin/dashboard/components/DashboardHero.vue` | `.hero-banner-card` (line 138) |
| Stat Card Blue | `#EEF5FE` / `#2563EB` | `frontend/src/views/admin/dashboard/components/StatCard.vue` | `.is-primary-kpi.variant-blue` (lines 124-137) |
| Stat Card Green | `#EDFCF7` / `#10B981` | `frontend/src/views/admin/dashboard/components/StatCard.vue` | `.is-primary-kpi.variant-green` (lines 140-153) |
| Stat Card Purple | `#F7F3FE` / `#8B5CF6` | `frontend/src/views/admin/dashboard/components/StatCard.vue` | `.is-primary-kpi.variant-purple` (lines 156-169) |
| Stat Card Orange | `#FEF7EE` / `#F97316` | `frontend/src/views/admin/dashboard/components/StatCard.vue` | `.is-primary-kpi.variant-orange` (lines 172-185) |
| Stat Card Amber | `#FFFBEB` / `#F59E0B` | `frontend/src/views/admin/dashboard/components/StatCard.vue` | `.is-operational-kpi.variant-amber` (lines 192-210) |
| Stat Card Red | `#FEF2F2` / `#EF4444` | `frontend/src/views/admin/dashboard/components/StatCard.vue` | `.is-operational-kpi.variant-red` (lines 212-229) |
| Stat Card Emerald | `#ECFDF5` / `#10B981` | `frontend/src/views/admin/dashboard/components/StatCard.vue` | `.is-operational-kpi.variant-emerald` (lines 232-250) |
| Stat Card Violet | `#FAF5FF` / `#8B5CF6` | `frontend/src/views/admin/dashboard/components/StatCard.vue` | `.is-operational-kpi.variant-purple` (lines 252-270) |
| Primary Button | `#1E3A8A` | `frontend/src/assets/styles/main.css` | `.btn-primary` (lines 86-95) |
| Input Border Focus | `#3B82F6` | `frontend/src/components/common/InputField.vue` | `.form-control:focus` (line 152) |
| Input Error State | `#EF4444` | `frontend/src/components/common/InputField.vue` | `.has-error .form-control` (line 163) |

---

## 6. Final Core Brand Summary

| Semantic Role | Target Element | HEX Code | RGB Value | Purpose |
|---|---|---|---|---|
| **Primary Brand Color** | Core actions & button anchors | `#1E3A8A` | `rgb(30, 58, 138)` | Deep Oxford Navy establishing institutional trust |
| **Secondary Brand Color** | Accents & hero banner endpoint | `#0284C7` | `rgb(2, 132, 199)` | Modern Vivid Sky Blue |
| **Accent Interactive Color** | Active sidebar navigation & CTA | `#FF5722` | `rgb(255, 87, 34)` | High-energy Solar Orange pill with glowing shadow |
| **Sidebar Background** | Main navigation drawer | `#0A192F` | `rgb(10, 25, 47)` | Deep Midnight Navy |
| **Header Background** | Top fixed navigation navbar | `#FFFFFF` | `rgb(255, 255, 255)` | Pure Clean White |
| **Main Page Background** | Full-portal background canvas | `#F8FAFC` | `rgb(248, 250, 252)` | Slate 50 ultra-light canvas |
| **Card Surface Color** | Standard card, table & modal surface | `#FFFFFF` | `rgb(255, 255, 255)` | Elevated pure white surface |
| **Primary Text Color** | Titles, headings & primary numbers | `#0F172A` | `rgb(15, 23, 42)` | Deep Slate 900 |
| **Secondary Text Color** | Column headers & table cells | `#475569` | `rgb(71, 85, 105)` | Slate 600 |
| **Main Border Color** | Dividers, separators & cards | `#E2E8F0` | `rgb(226, 232, 240)` | Slate 200 subtle divider |

---
*Generated by Antigravity Frontend & UI/UX Audit System.*

