"""
Management command to seed the database with realistic mock data for testing.

Generates:
  - 5 extra test users (mix of manager/user roles)
  - 30 announcements across all departments and types
  - Programmatically generated banner images via Pillow
  - Varied statuses (active / inactive)
  - Realistic titles and descriptions

Usage:
  python manage.py seed_mock_data
  python manage.py seed_mock_data --clear    # wipe announcements first
  python manage.py seed_mock_data --count 50  # custom announcement count
"""
import io
import random
from datetime import timedelta

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


# ---------------------------------------------------------------------------
# Colour palette per department  (background, text)
# ---------------------------------------------------------------------------
DEPT_COLORS = {
    'IT':          ('#1E3A5F', '#E8F4FD'),
    'HR':          ('#4A1942', '#FCE4EC'),
    'Marketing':   ('#1B4332', '#D8F3DC'),
    'Finance':     ('#7B3F00', '#FFF3E0'),
    'Operations':  ('#1A237E', '#E8EAF6'),
}

TYPE_BADGE_COLORS = {
    'General':       '#4CAF50',
    'Urgent':        '#F44336',
    'Event':         '#2196F3',
    'Policy Update': '#FF9800',
    'Maintenance':   '#9C27B0',
}

# ---------------------------------------------------------------------------
# Mock announcement data
# ---------------------------------------------------------------------------
MOCK_ANNOUNCEMENTS = [
    # ── IT ──────────────────────────────────────────────────────────────────
    {
        'title': 'Scheduled System Maintenance – March 10',
        'description': (
            'Our infrastructure team will be performing scheduled maintenance on all '
            'production servers on March 10, 2026 from 02:00 to 06:00 UTC.\n\n'
            'During this window, the following services will be temporarily unavailable:\n'
            '• Internal HR portal\n'
            '• Finance reporting dashboard\n'
            '• Email archiving system\n\n'
            'Please save all your work and log out before the maintenance window begins. '
            'We apologise for any inconvenience this may cause.'
        ),
        'department': 'IT',
        'type': 'Maintenance',
        'status': 'active',
    },
    {
        'title': 'New VPN Policy – Mandatory Update Required',
        'description': (
            'Effective March 20, 2026, all remote employees must upgrade their VPN client '
            'to version 5.4 or later.\n\n'
            'The legacy VPN client (v4.x) will be decommissioned and connections will be '
            'blocked after this date.\n\n'
            'To update:\n'
            '1. Visit the IT Self-Service Portal at https://it.internal/vpn\n'
            '2. Download the latest installer for your OS\n'
            '3. Follow the on-screen instructions\n\n'
            'Contact the IT helpdesk at ext. 1001 if you encounter any issues.'
        ),
        'department': 'IT',
        'type': 'Policy Update',
        'status': 'active',
    },
    {
        'title': 'New Software Licenses Available – Adobe Creative Suite',
        'description': (
            'The IT department has procured 20 additional licences for Adobe Creative Suite 2026.\n\n'
            'These licences are available to teams in Marketing, Design, and Communications. '
            'To request a licence, submit a ticket through the IT portal with the subject line '
            '"Adobe CC Licence Request" and include your manager\'s approval.\n\n'
            'Licences will be allocated on a first-come, first-served basis.\n'
            'For questions, contact it-software@company.com.'
        ),
        'department': 'IT',
        'type': 'General',
        'status': 'active',
    },
    {
        'title': 'Phishing Alert – Suspicious Emails Detected',
        'description': (
            'URGENT: Our security team has detected a phishing campaign targeting company email '
            'addresses.\n\n'
            'If you receive an email claiming to be from "IT Support" asking for your login '
            'credentials or asking you to click a password-reset link, DO NOT interact with it.\n\n'
            'What to do:\n'
            '• Do NOT click any links\n'
            '• Do NOT provide credentials\n'
            '• Forward the email to security@company.com immediately\n'
            '• Delete the email from your inbox\n\n'
            'The IT Security team is actively investigating. Stay vigilant.'
        ),
        'department': 'IT',
        'type': 'Urgent',
        'status': 'active',
    },
    {
        'title': 'Cloud Migration Project Kickoff – Q2 2026',
        'description': (
            'We are pleased to announce the official kickoff of the Cloud Migration Project. '
            'Over the next three quarters, we will migrate our on-premises infrastructure to '
            'AWS.\n\n'
            'Phase 1 (April – June): Development and staging environments\n'
            'Phase 2 (July – September): Internal tools and databases\n'
            'Phase 3 (October – December): Production workloads\n\n'
            'A town-hall session will be held on April 5th at 10:00 AM in Conference Room A '
            'for all stakeholders. Attendance is strongly encouraged.'
        ),
        'department': 'IT',
        'type': 'Event',
        'status': 'active',
    },

    # ── HR ──────────────────────────────────────────────────────────────────
    {
        'title': 'Updated Annual Leave Policy – Effective April 1, 2026',
        'description': (
            'Following a review of our benefits package, we are updating the Annual Leave '
            'Policy effective April 1, 2026.\n\n'
            'Key changes:\n'
            '• All full-time employees will receive 25 days annual leave (up from 22)\n'
            '• Part-time employees will receive a pro-rated increase\n'
            '• Unused leave can be carried over up to a maximum of 10 days\n'
            '• The leave year remains January 1 – December 31\n\n'
            'The updated policy document is available on the HR portal. Please review it and '
            'direct any questions to hr@company.com.'
        ),
        'department': 'HR',
        'type': 'Policy Update',
        'status': 'active',
    },
    {
        'title': 'Company Wellness Week – March 16–20, 2026',
        'description': (
            'We are excited to announce our annual Wellness Week taking place March 16–20, 2026!\n\n'
            'This year\'s programme includes:\n'
            '• Monday: Mindfulness and meditation sessions (10:00 AM, yoga studio)\n'
            '• Tuesday: Nutrition workshop with a registered dietitian (12:00 PM, cafeteria)\n'
            '• Wednesday: Step challenge – track your steps all day!\n'
            '• Thursday: Financial wellbeing webinar (2:00 PM, online)\n'
            '• Friday: Team yoga session (8:30 AM, rooftop terrace)\n\n'
            'All sessions are free and open to all employees. Register at wellness.internal.'
        ),
        'department': 'HR',
        'type': 'Event',
        'status': 'active',
    },
    {
        'title': 'Performance Review Cycle Opens – Q1 2026',
        'description': (
            'The Q1 2026 Performance Review cycle is now open in the HR system.\n\n'
            'Timeline:\n'
            '• March 4 – March 18: Self-assessment submission\n'
            '• March 19 – April 4: Manager reviews\n'
            '• April 7 – April 18: Calibration sessions\n'
            '• April 21 onwards: Employee feedback meetings\n\n'
            'All employees must complete their self-assessment by March 18. Log in to the HR '
            'portal at hr.internal to begin.\n\n'
            'For guidance, refer to the Performance Review Guide on the HR resources page.'
        ),
        'department': 'HR',
        'type': 'General',
        'status': 'active',
    },
    {
        'title': 'Mandatory Compliance Training – Deadline March 31',
        'description': (
            'REMINDER: All employees are required to complete the following mandatory compliance '
            'training modules by March 31, 2026:\n\n'
            '1. Data Protection & GDPR Refresher (45 min)\n'
            '2. Anti-Bribery and Corruption (30 min)\n'
            '3. Workplace Health & Safety (60 min)\n'
            '4. Code of Conduct 2026 Update (20 min)\n\n'
            'Failure to complete these modules by the deadline may result in system access '
            'restrictions.\n\n'
            'Access the training portal at training.internal using your company SSO credentials.'
        ),
        'department': 'HR',
        'type': 'Urgent',
        'status': 'active',
    },
    {
        'title': 'Employee Referral Programme – New Bonus Structure',
        'description': (
            'We are updating our Employee Referral Programme with an improved bonus structure, '
            'effective immediately.\n\n'
            'New referral bonuses:\n'
            '• Junior roles (Grade 1–3): £1,000\n'
            '• Mid-level roles (Grade 4–6): £2,000\n'
            '• Senior roles (Grade 7+): £3,500\n'
            '• Director and above: £5,000\n\n'
            'Bonuses are paid 3 months after the referred employee\'s start date, subject to '
            'both parties remaining in employment.\n\n'
            'Refer a friend via the HR portal today!'
        ),
        'department': 'HR',
        'type': 'General',
        'status': 'active',
    },

    # ── Marketing ────────────────────────────────────────────────────────────
    {
        'title': 'Q2 2026 Marketing Calendar Published',
        'description': (
            'The Marketing team has published the Q2 2026 campaign and content calendar.\n\n'
            'Highlights:\n'
            '• April: Product relaunch campaign for the Enterprise product line\n'
            '• May: Customer Appreciation Month – loyalty programme promotions\n'
            '• June: Mid-year brand refresh rollout\n\n'
            'The full calendar with deadlines, asset requirements, and stakeholder responsibilities '
            'is available at confluence.internal/marketing/q2-2026.\n\n'
            'Kick-off meeting for all marketing contributors is scheduled for March 9 at 2:00 PM.'
        ),
        'department': 'Marketing',
        'type': 'General',
        'status': 'active',
    },
    {
        'title': 'Product Launch Party – New Platform Release 🚀',
        'description': (
            'Join us to celebrate the launch of our new platform!\n\n'
            'Event details:\n'
            '📅 Date: Friday, April 18, 2026\n'
            '⏰ Time: 6:00 PM – 9:00 PM\n'
            '📍 Venue: The Rooftop Lounge, 12th Floor\n\n'
            'There will be a live demo of the new features, followed by drinks and dinner. '
            'Bring a plus-one – the more the merrier!\n\n'
            'RSVP by April 10 via the events portal at events.internal/platform-launch. '
            'Space is limited to 150 guests.'
        ),
        'department': 'Marketing',
        'type': 'Event',
        'status': 'active',
    },
    {
        'title': 'Brand Guidelines Updated – Version 4.0',
        'description': (
            'The Marketing team has released an updated version of the Company Brand Guidelines '
            '(v4.0).\n\n'
            'What\'s new in v4.0:\n'
            '• Refreshed colour palette with updated HEX, RGB, and CMYK values\n'
            '• New typography stack (Inter replaces Helvetica for digital assets)\n'
            '• Updated logo usage rules and exclusion zones\n'
            '• New icon library integrated with Figma and Adobe XD\n'
            '• Social media asset templates\n\n'
            'Download the full guidelines from the Brand Hub at brand.internal.\n'
            'Questions? Contact brand@company.com.'
        ),
        'department': 'Marketing',
        'type': 'Policy Update',
        'status': 'active',
    },
    {
        'title': 'Social Media Policy Reminder',
        'description': (
            'As a reminder, all employees who represent the company on social media must adhere '
            'to the Social Media Policy (available on the HR portal).\n\n'
            'Key points:\n'
            '• You must not disclose confidential company information\n'
            '• Do not engage with negative press or competitor posts on behalf of the company\n'
            '• Always add a disclaimer when sharing personal opinions on industry topics\n'
            '• Report any social media crises or brand mentions to marketing@company.com\n\n'
            'The full policy document was last updated January 2026.'
        ),
        'department': 'Marketing',
        'type': 'Policy Update',
        'status': 'inactive',
    },
    {
        'title': 'Industry Conference – Sponsorship Opportunity',
        'description': (
            'We have been offered a Gold Sponsorship package at TechSummit 2026, taking place '
            'in London on May 14–15, 2026.\n\n'
            'The sponsorship includes:\n'
            '• Branded exhibition booth (12 sqm)\n'
            '• 2 speaking slots (30 minutes each)\n'
            '• Logo placement on all event materials\n'
            '• 10 complimentary delegate passes\n\n'
            'We are seeking 4 team members to represent the company at the booth and one speaker '
            'for each session slot.\n\n'
            'Interested? Express your interest to marketing@company.com by March 15.'
        ),
        'department': 'Marketing',
        'type': 'Event',
        'status': 'active',
    },

    # ── Finance ──────────────────────────────────────────────────────────────
    {
        'title': 'Year-End Financial Close – Key Deadlines',
        'description': (
            'The Finance team is initiating the year-end close process. Please ensure all '
            'outstanding items are addressed by the following deadlines:\n\n'
            '• March 7: All expense reports submitted and approved\n'
            '• March 10: Purchase orders closed or carried forward\n'
            '• March 14: Final journal entries submitted\n'
            '• March 18: Departmental budget variance reports due\n'
            '• March 28: Auditor access period begins\n\n'
            'Contact your finance business partner for department-specific guidance. '
            'Late submissions will not be processed in this fiscal year.'
        ),
        'department': 'Finance',
        'type': 'Urgent',
        'status': 'active',
    },
    {
        'title': 'New Expense Reimbursement Policy – Effective April 1',
        'description': (
            'The updated Expense Reimbursement Policy will take effect on April 1, 2026.\n\n'
            'Key changes:\n'
            '• Meal allowance increased to £35/day (domestic) and £55/day (international)\n'
            '• Hotel limits raised to £180/night (London) and £130/night (other UK cities)\n'
            '• All expenses above £75 must be submitted within 30 days\n'
            '• Receipts are now mandatory for all claims above £10 (previously £20)\n'
            '• Expenses must be submitted via Concur (paper forms no longer accepted)\n\n'
            'A training session on Concur will be held March 20 at 11:00 AM. Register at '
            'training.internal.'
        ),
        'department': 'Finance',
        'type': 'Policy Update',
        'status': 'active',
    },
    {
        'title': 'Q4 2025 Budget Review Results',
        'description': (
            'The Finance team has completed the Q4 2025 budget review. Key findings:\n\n'
            '• Overall company spend came in 3.2% under budget\n'
            '• IT infrastructure savings: £142,000 due to cloud optimisation\n'
            '• Marketing overspent by £28,000 (campaign acceleration approved by exec)\n'
            '• Operations delivered £95,000 in procurement savings\n\n'
            'Department heads will receive detailed variance reports by March 8. '
            'The full board-level summary will be shared in the All-Hands meeting on March 12.'
        ),
        'department': 'Finance',
        'type': 'General',
        'status': 'active',
    },
    {
        'title': 'Payroll Processing Date Change – March 2026',
        'description': (
            'Please note that the March 2026 payroll will be processed one day earlier than usual '
            'due to the bank holiday on March 27.\n\n'
            'Updated schedule:\n'
            '• Payroll submission deadline: March 19 (instead of March 20)\n'
            '• Processing date: March 25 (instead of March 26)\n'
            '• Expected payment in accounts: March 26\n\n'
            'Please ensure all timesheets, overtime claims, and commission updates are submitted '
            'by 5:00 PM on March 19. Late submissions will be processed in April.'
        ),
        'department': 'Finance',
        'type': 'General',
        'status': 'active',
    },
    {
        'title': 'Finance System Downtime – Concur Upgrade',
        'description': (
            'The Concur expense management system will be offline for a planned upgrade on '
            'Saturday, March 14, 2026 from 06:00 to 14:00 UTC.\n\n'
            'During this window:\n'
            '• Expense submissions will be unavailable\n'
            '• Approval workflows will be paused\n'
            '• Report exports will be disabled\n\n'
            'Please plan accordingly and submit any urgent expense reports before Saturday morning. '
            'The upgrade brings improved mobile functionality and faster report processing.'
        ),
        'department': 'Finance',
        'type': 'Maintenance',
        'status': 'active',
    },

    # ── Operations ───────────────────────────────────────────────────────────
    {
        'title': 'New Office Access Policy – Security Badges',
        'description': (
            'Effective March 15, 2026, all employees must use their security badge to access '
            'all floors, including the ground floor reception.\n\n'
            'What this means for you:\n'
            '• You must have your badge with you at all times on company premises\n'
            '• Tailgating (following someone through a secure door) is strictly prohibited\n'
            '• Lost or stolen badges must be reported to security immediately at ext. 999\n\n'
            'New badges have been issued to all staff via internal mail this week. '
            'If you have not received yours, contact facilities@company.com.'
        ),
        'department': 'Operations',
        'type': 'Policy Update',
        'status': 'active',
    },
    {
        'title': 'Office Relocation – Floor 8 Moving to Floor 11',
        'description': (
            'The Operations and Finance teams currently occupying Floor 8 will relocate to '
            'the newly refurbished Floor 11 over the weekend of March 21–22, 2026.\n\n'
            'What to do:\n'
            '• Pack all personal items in the boxes provided by end of day March 20\n'
            '• Label boxes with your name and new desk number (assigned via email from Facilities)\n'
            '• Do not pack IT equipment — IT will handle monitor and docking station moves\n\n'
            'The new floor features hot-desking zones, private focus booths, and a communal '
            'kitchen. Full floor plan available at facilities.internal.'
        ),
        'department': 'Operations',
        'type': 'General',
        'status': 'active',
    },
    {
        'title': 'Fire Drill – March 12, 2026 at 11:00 AM',
        'description': (
            'A mandatory fire drill will take place on Wednesday, March 12, 2026 at 11:00 AM.\n\n'
            'Instructions:\n'
            '• When the alarm sounds, immediately stop all work\n'
            '• Do not use the lifts — use the fire exits on your floor\n'
            '• Proceed to the designated assembly point: Car Park B on Wellington Street\n'
            '• Floor wardens will conduct a headcount at the assembly point\n'
            '• Do not re-enter the building until the all-clear is given\n\n'
            'The drill is expected to last approximately 20 minutes. '
            'Please do not schedule client calls during this period.'
        ),
        'department': 'Operations',
        'type': 'Urgent',
        'status': 'active',
    },
    {
        'title': 'Procurement Vendor Review 2026 – Invitation for Nominations',
        'description': (
            'The Operations team is conducting its annual vendor review for 2026. We are inviting '
            'all departments to nominate new suppliers for evaluation.\n\n'
            'We are particularly interested in suppliers specialising in:\n'
            '• Cloud and SaaS tools\n'
            '• Office supplies and facilities management\n'
            '• Professional training and development services\n'
            '• Event management and catering\n\n'
            'Nominations must be submitted via the procurement portal at procurement.internal '
            'by March 20, 2026. Shortlisted vendors will be invited for demos in April.'
        ),
        'department': 'Operations',
        'type': 'General',
        'status': 'active',
    },
    {
        'title': 'Catering Service Change – New Provider Starting April 1',
        'description': (
            'We are pleased to announce that Fresh & Co. will be taking over as the company\'s '
            'catering provider from April 1, 2026.\n\n'
            'The new service includes:\n'
            '• Expanded breakfast menu (7:30–9:30 AM)\n'
            '• Hot lunch options with rotating daily specials (12:00–2:00 PM)\n'
            '• Allergen-clearly-labelled menus\n'
            '• Vegan and vegetarian options at every meal\n'
            '• Pre-ordering available via the Fresh & Co. app\n\n'
            'A tasting event will be held on March 25 in the cafeteria from 12:00–2:00 PM. '
            'All are welcome!'
        ),
        'department': 'Operations',
        'type': 'Event',
        'status': 'active',
    },

    # ── Extra cross-department inactive items ────────────────────────────────
    {
        'title': 'System Upgrade Completed – Legacy CRM Decommissioned',
        'description': (
            'The legacy CRM system (SalesTrack v2) has been officially decommissioned as of '
            'March 1, 2026. All data has been migrated to the new Salesforce Enterprise instance.\n\n'
            'If you encounter any missing records or data discrepancies, please raise a ticket '
            'in the IT portal immediately with the prefix [CRM-MIGRATION].\n\n'
            'Training recordings for the new CRM system are available at learning.internal/crm.'
        ),
        'department': 'IT',
        'type': 'General',
        'status': 'inactive',
    },
    {
        'title': 'End of Year Party 2025 – Thank You!',
        'description': (
            'A huge thank you to everyone who attended the End of Year Party 2025!\n\n'
            'We had over 280 attendees and raised £3,400 for our charity partner, The Children\'s '
            'Trust. The raffle, silent auction, and live band made for a fantastic evening.\n\n'
            'Photos from the event are available in the company SharePoint under '
            'Company Events > 2025 > Year-End Party.\n\n'
            'We look forward to an even bigger celebration at the end of 2026!'
        ),
        'department': 'HR',
        'type': 'Event',
        'status': 'inactive',
    },
    {
        'title': 'Q3 2025 Financial Results – Employee Summary',
        'description': (
            'We are pleased to share the Q3 2025 financial results with all employees.\n\n'
            'Highlights:\n'
            '• Revenue: £24.7M (+12% YoY)\n'
            '• Gross margin: 68% (up from 64% in Q3 2024)\n'
            '• New customers: 142 (record high)\n'
            '• Net Promoter Score: 61 (industry average: 42)\n\n'
            'The CEO will present a full breakdown including forward-looking guidance at the '
            'All-Hands meeting this Thursday at 3:00 PM. The session will also be livestreamed '
            'for remote employees.'
        ),
        'department': 'Finance',
        'type': 'General',
        'status': 'inactive',
    },
    {
        'title': 'Summer Internship Programme 2026 – Applications Now Open',
        'description': (
            'We are now accepting applications for our Summer Internship Programme 2026.\n\n'
            'This year we are offering placements in:\n'
            '• Software Engineering (5 positions)\n'
            '• Data Analytics (3 positions)\n'
            '• Marketing & Brand (2 positions)\n'
            '• Finance & Accounting (2 positions)\n'
            '• Operations & Strategy (2 positions)\n\n'
            'Duration: 10 weeks (June 8 – August 14, 2026)\n'
            'Eligibility: Penultimate-year undergraduate students\n\n'
            'Apply at careers.company.com/internships. Application deadline: April 11, 2026.'
        ),
        'department': 'HR',
        'type': 'General',
        'status': 'active',
    },
    {
        'title': 'Marketing Automation Platform Migration Complete',
        'description': (
            'We have successfully migrated from Mailchimp to HubSpot Marketing Hub as of '
            'March 1, 2026. All campaigns, contact lists, and automation workflows have been '
            'transferred.\n\n'
            'Training materials to help you get started with HubSpot are available at '
            'confluence.internal/marketing/hubspot-guides.\n\n'
            'A live Q&A session for marketing team members will be held March 10 at 3:00 PM. '
            'Book your slot via the calendar invite sent to marketing@company.com.\n\n'
            'For urgent support during the transition period, contact martech@company.com.'
        ),
        'department': 'Marketing',
        'type': 'General',
        'status': 'active',
    },
]

# ---------------------------------------------------------------------------
# Extra test users
# ---------------------------------------------------------------------------
EXTRA_USERS = [
    {'username': 'alice_manager', 'email': 'alice@example.com', 'first_name': 'Alice',
     'last_name': 'Johnson', 'role': 'manager'},
    {'username': 'bob_manager',   'email': 'bob@example.com',   'first_name': 'Bob',
     'last_name': 'Williams',  'role': 'manager'},
    {'username': 'carol_user',    'email': 'carol@example.com', 'first_name': 'Carol',
     'last_name': 'Davis',     'role': 'user'},
    {'username': 'dan_user',      'email': 'dan@example.com',   'first_name': 'Dan',
     'last_name': 'Brown',     'role': 'user'},
    {'username': 'eve_user',      'email': 'eve@example.com',   'first_name': 'Eve',
     'last_name': 'Wilson',    'role': 'user'},
]


def _hex_to_rgb(hex_color: str):
    """Convert '#RRGGBB' to (R, G, B) tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def generate_announcement_image(title: str, dept_name: str, type_name: str) -> ContentFile:
    """
    Generate a 800×400 banner image for an announcement using Pillow.

    Layout:
      - Solid dark background (department colour)
      - Gradient overlay strip at the bottom
      - Coloured type badge (top-left)
      - Department name (top-right)
      - Title text (centre)
    """
    width, height = 800, 400

    bg_raw, fg_raw = DEPT_COLORS.get(dept_name, ('#2C3E50', '#ECF0F1'))
    bg_color = _hex_to_rgb(bg_raw)
    fg_color = _hex_to_rgb(fg_raw)
    badge_color = _hex_to_rgb(TYPE_BADGE_COLORS.get(type_name, '#607D8B'))

    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Subtle gradient overlay at the bottom third
    for y in range(height // 2, height):
        alpha = int(80 * (y - height // 2) / (height // 2))
        overlay = tuple(max(0, c - alpha) for c in bg_color)
        draw.line([(0, y), (width, y)], fill=overlay)

    # Decorative accent bar (left edge)
    draw.rectangle([(0, 0), (8, height)], fill=badge_color)

    # Type badge (top-left)
    badge_padding = 10
    badge_x, badge_y = 24, 24
    badge_text = type_name.upper()
    badge_w = len(badge_text) * 9 + badge_padding * 2
    badge_h = 32
    draw.rounded_rectangle(
        [(badge_x, badge_y), (badge_x + badge_w, badge_y + badge_h)],
        radius=6,
        fill=badge_color,
    )
    draw.text(
        (badge_x + badge_padding, badge_y + 7),
        badge_text,
        fill=(255, 255, 255),
    )

    # Department name (top-right)
    dept_text = dept_name.upper()
    dept_text_w = len(dept_text) * 10
    draw.text(
        (width - dept_text_w - 24, 32),
        dept_text,
        fill=tuple(max(0, c - 40) for c in fg_color),
    )

    # Horizontal divider
    draw.line([(24, 80), (width - 24, 80)], fill=badge_color, width=2)

    # Main title  — wrap long lines
    max_chars_per_line = 36
    words = title.split()
    lines = []
    current = ''
    for word in words:
        if len(current) + len(word) + 1 <= max_chars_per_line:
            current = (current + ' ' + word).strip()
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    line_height = 48
    total_text_h = len(lines) * line_height
    start_y = (height - total_text_h) // 2 + 10

    for i, line in enumerate(lines):
        text_w = len(line) * 18
        text_x = (width - text_w) // 2
        text_y = start_y + i * line_height
        # Shadow
        draw.text((text_x + 2, text_y + 2), line, fill=(0, 0, 0, 80))
        # Main text
        draw.text((text_x, text_y), line, fill=fg_color)

    # Bottom label
    bottom_label = 'ANNOUNCEMENT MANAGEMENT PLATFORM'
    bottom_w = len(bottom_label) * 7
    draw.text(
        ((width - bottom_w) // 2, height - 30),
        bottom_label,
        fill=tuple(max(0, c - 60) for c in fg_color),
    )

    # Save to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='PNG', optimize=True)
    buffer.seek(0)
    safe_title = ''.join(c if c.isalnum() else '_' for c in title[:30]).lower()
    filename = f'mock_{safe_title}.png'
    return ContentFile(buffer.read(), name=filename)


class Command(BaseCommand):
    help = 'Seed the database with realistic mock announcements and test users.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            default=False,
            help='Delete all existing announcements before seeding.',
        )
        parser.add_argument(
            '--no-images',
            action='store_true',
            default=False,
            help='Skip image generation (faster seeding).',
        )

    def handle(self, *args, **options):
        if not PILLOW_AVAILABLE:
            self.stdout.write(
                self.style.WARNING('Pillow not installed — images will be skipped.')
            )

        self.stdout.write(self.style.MIGRATE_HEADING('\n🌱  Seeding mock data...\n'))

        # ── Clear existing announcements if requested ──────────────────────
        if options['clear']:
            from announcements.models import Announcement
            count, _ = Announcement.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'  Deleted {count} existing announcements.'))

        # ── Ensure base seed data exists ───────────────────────────────────
        self._ensure_base_data()

        # ── Create extra test users ────────────────────────────────────────
        managers = self._create_extra_users()

        # ── Create announcements ───────────────────────────────────────────
        skip_images = options['no_images'] or not PILLOW_AVAILABLE
        created_count = self._create_announcements(managers, skip_images)

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅  Done! Created {created_count} mock announcements.\n'
            )
        )

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    def _ensure_base_data(self):
        """Make sure departments and announcement types exist."""
        from django.contrib.auth import get_user_model
        from announcement_types.models import AnnouncementType
        from departments.models import Department
        from accounts.management.commands.seed_data import (

            DEFAULT_ANNOUNCEMENT_TYPES,
            DEFAULT_DEPARTMENTS,
        )
        for dept_data in DEFAULT_DEPARTMENTS:
            Department.objects.get_or_create(name=dept_data['name'], defaults=dept_data)
        for type_data in DEFAULT_ANNOUNCEMENT_TYPES:
            AnnouncementType.objects.get_or_create(name=type_data['name'], defaults=type_data)

        User = get_user_model()
        # Ensure the base manager account exists
        manager, created = User.objects.get_or_create(
            username='manager',
            defaults={
                'email': 'manager@example.com',
                'first_name': 'System',
                'last_name': 'Manager',
                'role': 'manager',
                'is_staff': True,
            },
        )
        if created:
            manager.set_password('manager123')
            manager.save()
            self.stdout.write('  Created base manager account.')

    def _create_extra_users(self):
        """Create extra test users and return list of manager users."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        managers = list(User.objects.filter(role='manager'))

        for data in EXTRA_USERS:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': data['role'],
                },
            )
            if created:
                user.set_password('TestPass123!')
                user.save()
                status_label = 'Created'
            else:
                status_label = 'Already exists'

            self.stdout.write(
                f'  User [{data["role"]:7}]: {data["username"]:20} — {status_label}'
            )

            if data['role'] == 'manager' and user not in managers:
                managers.append(user)

        return managers

    def _create_announcements(self, managers: list, skip_images: bool) -> int:
        """Create all mock announcements and return count of newly created ones."""
        from announcement_types.models import AnnouncementType
        from announcements.models import Announcement
        from departments.models import Department

        dept_cache = {d.name: d for d in Department.objects.all()}
        type_cache = {t.name: t for t in AnnouncementType.objects.all()}

        created_count = 0
        # Spread created_at timestamps over the past 90 days so list ordering looks realistic
        now = timezone.now()

        self.stdout.write('')

        for i, data in enumerate(MOCK_ANNOUNCEMENTS):
            dept = dept_cache.get(data['department'])
            atype = type_cache.get(data['type'])

            if not dept or not atype:
                self.stdout.write(
                    self.style.WARNING(
                        f'  Skipping "{data["title"]}" — department or type not found.'
                    )
                )
                continue

            if Announcement.objects.filter(title=data['title']).exists():
                self.stdout.write(f'  Skip (exists): {data["title"][:60]}')
                continue

            # Pick a random manager as author
            author = random.choice(managers) if managers else None

            announcement = Announcement(
                title=data['title'],
                description=data['description'],
                type=atype,
                department=dept,
                status=data.get('status', 'active'),
                created_by=author,
            )

            # Attach generated image
            if not skip_images:
                try:
                    img_file = generate_announcement_image(
                        data['title'], data['department'], data['type']
                    )
                    announcement.image.save(img_file.name, img_file, save=False)
                except Exception as exc:
                    self.stdout.write(
                        self.style.WARNING(f'    Image generation failed: {exc}')
                    )

            announcement.save()

            # Backdate created_at so entries are spread across 90 days
            days_ago = int(90 * i / len(MOCK_ANNOUNCEMENTS))
            Announcement.objects.filter(pk=announcement.pk).update(
                created_at=now - timedelta(days=days_ago),
            )

            created_count += 1
            badge = '🟢' if data['status'] == 'active' else '⚪'
            self.stdout.write(
                f'  {badge} [{data["department"]:12}] [{data["type"]:14}] '
                f'{data["title"][:55]}'
            )

        return created_count
