# MediSite Clinic

This document serves as the **authoritative CHANGELOG and TECHNICAL DOCUMENTATION** for the MediSite Clinic Odoo module.

It will be **continuously updated** as development progresses. Each change should be appended (never rewritten) to preserve historical accuracy.

---

## CHANGELOG

### [1.0.0] – Initial Stable Baseline

**Status:** Stable

#### Added

* Core models:

  * `med.patient` – Patient registry with demographic data and computed age
  * `med.staff` – Medical staff registry with role-based login creation
  * `med.consultation` – Central clinical encounter model
  * `med.consultation.audit` – Immutable audit trail for clinical actions

* Role-based workflow:

  * Nurse → Doctor → Lab → Doctor → Completed
  * Enforced via UI controls, Python guards, and security groups

* Clinical sections implemented:

  * Nurse history and vitals
  * Lab / side room investigations
  * Doctor examination and assessment
  * Diagnosis, treatment, follow-up, and escalation

* Data integrity features:

  * Nurse-entered data locked after transition to Doctor stage
  * Field-level write protection
  * Automatic audit logging for tracked clinical fields

* Audit trail system:

  * Tracks user, role, action, field changes, timestamps
  * Read-only by default for non-admin users

* Attachments:

  * External hospital documents linked via `ir.attachment`

* UI components:

  * Form and tree views for Patients, Staff, Consultations
  * Notebook-based clinical sections
  * Previous consultations view for doctors

* Security:

  * Dedicated groups: Nurse, Doctor, Lab Technician, Admin
  * Granular access rules per role

#### Fixed

* Removed dangling reference to deprecated `med.pharmacy.order` model that caused registry load failure

### [1.1.0] – Pharmacy Order Locking

**Status:** Stable

#### Added

* Pharmacy order immutability after dispensing
* Backend write protection on:
  * Order header fields
  * Order line items
* Deletion prevention for dispensed and paid orders
* UI-level readonly enforcement for dispensed orders

#### Security

* Prevents post-dispensing tampering
* Enforces real-world pharmacy compliance
* Protects financial and clinical integrity

---
# Pharmacy Module Changelog

## [1.2.0] – 2025-12-22
### Added
- Stock deduction implemented on dispensing pharmacy orders.
- Stock movement logging (`med.pharmacy.stock.move`) for every dispensed order.
- Computed total amount (`amount_total`) in `med.pharmacy.order`.
- Admin-only deletion added for:
  - Pharmacy orders (`med.pharmacy.order`)
  - Pharmacy order lines (`med.pharmacy.order.line`)
  - Stock movements (`med.pharmacy.stock.move`)
- Access rights updated:
  - Pharmacy users can create/write orders but cannot delete dispensed orders or stock movements.
  - Admin users have full CRUD access to pharmacy orders, order lines, products, and stock movements.

### Changed
- Locked `dispensed` and `paid` orders:
  - Cannot modify order header fields (consultation, patient, pharmacist).
  - Cannot modify or delete order lines.
  - Cannot delete dispensed or paid orders.
- UI updates:
  - Quantity available (`qty_available`) visible on product form view.
  - Improved tree and form views for pharmacy orders and products.

### Fixed
- Fixed missing stock deduction and stock movement logging in previous version.
- Fixed XML syntax errors in `med_pharmacy_product_views.xml`.


# Medisite Clinic Module - Changelog

All notable changes to this module will be documented in this file.

## [2026-01-12] - Version 1.0.0
### Added
- `med.patient` model:
  - Fields: `name`, `file_number`, `dob`, `age`, `gender`, `nationality`, `occupation`, `employer`, `photo`, `employee_id`.
  - Computed field `age` based on `dob`.
  - Relations: `ipd_ids` (One2many to IPD), `consultation_ids` (One2many to consultations).

- Patient Views:
  - Form view with split layout (details + photo) and notebook containing `Consultations` and `IPD Admissions`.
  - Tree view for listing patients with image avatars.

- `med.consultation` model:
  - Fields covering patient info, nurse input, doctor assessment, lab results, treatment, follow-ups, pharmacy order link, and workflow `state`.
  - Workflow stages: `nurse` → `doctor` → `lab` → `done`.
  - Audit trail mechanism to track changes by user role.

- Consultation Views:
  - Form view with header buttons for workflow transitions (send to doctor, lab, complete, send to pharmacy).
  - Notebook with pages for `History`, `Vitals`, `Lab/Side Room`, `Doctor Assessment`, `Previous Consultations`, and `Audit Trail`.
  - Tree view for listing consultations.

- `med.ipd` model (IPD Admissions):
  - Fields: `name`, `patient_id`, `consultation_id`, `admission_date`, `discharge_date`, `room_number`, `bed_number`, `state`, `reason`, `notes`.
  - Workflow actions: `action_admit`, `action_discharge`.

- IPD Views:
  - Form view with patient info, admission details, notes, and workflow buttons.
  - Tree view with key patient info and state.
  - Kanban view for visually managing admissions:
    - Custom styling added while preserving Odoo clickability and responsiveness.

### Changed
- UI Improvements:
  - Reduced patient record size in tree views.
  - Added professional styling to IPD kanban cards:
    - Colored status badges (`Draft`, `Admitted`, `Discharged`).
    - Structured card body with patient info, room/bed, and admission date.
    - Ensured clickable cards, responsive layout, and mobile support.
  - Fixed previous issues where kanban cards were not clickable due to improper CSS overrides.

- Consultation creation:
  - IPD admission creation via consultation using `create_ipd()` method.
  - Workflow restrictions added to prevent invalid state transitions.

### Fixed
- XML parse errors related to `&nbsp;` in kanban templates.
- Clickability issues in IPD kanban caused by missing `oe_kanban_global_click` and `o_kanban_record` classes.
- Tree view size issues making records appear overly large in the UI.

### Notes
- Users must have proper group permissions (`med_nurse`, `med_doctor`, `med_lab`, `med_admin`) to access and interact with records.
- Audit trail ensures traceability of clinical data modifications.





## TECHNICAL DOCUMENTATION

### 1. System Overview

MediSite Clinic is a **role-driven outpatient clinical management system** built on Odoo 15. It models real-world clinic workflows with strict separation of duties, data locking, and medico-legal auditability.

The system is designed to be **extensible**, allowing pharmacy, billing, and insurance modules to be added later without refactoring core logic.

---

### 2. Core Design Principles

* Patient-centric data model
* Single consultation record per encounter
* State-driven workflow enforcement
* Field-level data locking (not blanket record locking)
* Full auditability of clinical changes
* Clear separation between HR (staff) and system access (users)

---

### 3. Data Models

#### 3.1 `med.patient`

Represents a registered patient.

Key fields:

* `name`, `file_number`
* `dob`, `age` (computed)
* `gender`, `nationality`, `occupation`, `employer`

Relationships:

* One2many → `med.consultation`

---

#### 3.2 `med.staff`

Represents medical and administrative personnel.

Key fields:

* Identity and contact information
* `role` (nurse, doctor, lab tech, admin)
* Optional link to `res.users`

Special logic:

* `action_create_user()` creates system login and assigns correct security groups

---

#### 3.3 `med.consultation`

Central clinical encounter record.

Responsibilities:

* Stores nurse intake, vitals, lab results, doctor assessment
* Enforces workflow states
* Locks nurse-entered fields after doctor review
* Triggers audit logging on tracked changes

Workflow states:

* `nurse`
* `doctor`
* `lab`
* `done`

---

#### 3.4 `med.consultation.audit`

Immutable audit log for clinical accountability.

Captured data:

* User and inferred clinical role
* Action type
* Field-level old and new values
* Timestamp and contextual notes

---

### 4. Workflow Enforcement

Workflow transitions are enforced at three layers:

1. **User Interface** – Button visibility and readonly attributes
2. **Business Logic** – Python validation before state changes
3. **Data Layer** – Write restrictions and audit logging

This prevents unauthorized modification of clinical data.

---

### 5. Security Model

Security is group-based:

* `group_med_nurse`
* `group_med_doctor`
* `group_med_lab`
* `group_med_admin`

Access rules restrict:

* Creation and modification rights
* Visibility of sensitive clinical sections
* Audit trail editing

---

### 6. Audit & Compliance Notes

* All clinically significant changes are logged
* Completed consultations are signed and timestamped
* Design supports medico-legal review and traceability

---

## MAINTENANCE RULES (IMPORTANT)

* Every functional or structural change **must be added to the CHANGELOG**
* Never delete old changelog entries
* Increment version numbers only after a stable milestone
* Document new models, workflows, or security changes immediately

---

### 7. Pharmacy Order Control

Pharmacy orders follow a controlled lifecycle:

**States:**
- `draft` → Editable
- `dispensed` → Locked
- `paid` → Locked (financially closed)

Once an order is dispensed:
- No structural or financial edits are permitted
- Order lines become immutable
- Records cannot be deleted

Enforcement is applied at:
1. UI level (readonly views)
2. Business logic (write/unlink guards)
3. Workflow validation

This design ensures auditability and prevents fraud or clinical discrepancies.

# Pharmacy Module Documentation

## Models

### med.pharmacy.product
- **Fields:** `name`, `strength`, `form`, `unit_price`, `qty_available`, `active`, `notes`.
- **Views:** Form & Tree views.
- **Purpose:** Manage pharmacy drug master records.
- **Note:** `qty_available` is now displayed in the form view.

### med.pharmacy.order
- **Fields:** `name`, `consultation_id`, `patient_id`, `pharmacist_id`, `line_ids`, `amount_total`, `currency_id`, `state`.
- **Workflow:**
  - `draft` → `dispensed` → `paid`.
  - `dispensed` orders deduct stock and log stock movement.
  - `paid` orders cannot be modified.
- **Constraints:**
  - Orders in `dispensed` or `paid` state cannot be deleted by pharmacy users.
  - Admin users can delete orders and stock movements.

### med.pharmacy.order.line
- **Fields:** `order_id`, `product_id`, `quantity`, `unit_price`, `subtotal`.
- **Constraints:**
  - Cannot modify or delete lines if parent order is `dispensed` or `paid`.
- **Computed Fields:** `subtotal = quantity * unit_price`.

### med.pharmacy.stock.move
- **Fields:** `product_id`, `order_id`, `patient_id`, `quantity`, `move_type`, `user_id`, `date`.
- **Purpose:** Log stock movements for dispensing (`out`) or restocking (`in`).

---

## Access Rights

| Model | Group | Read | Write | Create | Delete |
|-------|-------|------|-------|--------|--------|
| med.pharmacy.order | Pharmacy | 1 | 1 | 1 | 0 |
| med.pharmacy.order | Admin | 1 | 1 | 1 | 1 |
| med.pharmacy.order.line | Pharmacy | 1 | 1 | 1 | 0 |
| med.pharmacy.order.line | Admin | 1 | 1 | 1 | 1 |
| med.pharmacy.product | Admin | 1 | 1 | 1 | 1 |
| med.pharmacy.stock.move | Pharmacy | 1 | 0 | 0 | 0 |
| med.pharmacy.stock.move | Admin | 1 | 1 | 1 | 1 |

---

# Medisite Clinic Module - Technical Documentation

## 1. Module Overview
The `medisite_clinic` module is designed to manage **patients**, **consultations**, and **inpatient admissions (IPD)** in a clinical setting. It provides full workflow support for nurses, doctors, lab technicians, and administrators, including audit tracking and professional UI presentation.

Key features:
- Patient registry management with photo and demographic details.
- Consultation tracking with nurse input, doctor assessment, lab results, and follow-ups.
- IPD Admission workflow with kanban, form, and tree views.
- Audit trail of clinical actions.
- Professional, responsive UI with clickable kanban cards and improved tree view layout.

---

## 2. Models

### 2.1 Patient (`med.patient`)
**Purpose:** Central patient registry.

**Fields:**
- `name` (Char, required) — Patient full name.
- `file_number` (Char, indexed) — Unique file number for each patient.
- `dob` (Date) — Date of birth.
- `age` (Integer, computed) — Automatically computed from `dob`.
- `gender` (Selection) — 'm' (Male), 'f' (Female).
- `nationality` (Char)
- `occupation` (Char)
- `employer` (Char)
- `photo` (Binary) — Patient photo for UI display.
- `employee_id` (Char) — Optional employee identifier.

**Relations:**
- `ipd_ids` (One2many → `med.ipd`) — List of IPD admissions for this patient.
- `consultation_ids` (One2many → `med.consultation`) — List of consultations for this patient.

**Views:**
- **Form View:** Split layout with left column for patient details, right column for photo, and notebook pages for `Consultations` and `IPD Admissions`.
- **Tree View:** Displays avatar, name, file number, age, and gender. Optimized to reduce row height and improve readability.

---

### 2.2 Consultation (`med.consultation`)
**Purpose:** Track medical consultations and treatments.

**Fields:**
- `patient_id` (Many2one → `med.patient`) — Linked patient.
- `file_number` (related, Char) — Pulled from patient record.
- `patient_name` (related, Char) — Pulled from patient record.
- `date`, `time` (Datetime) — Defaulted to current.
- Nurse fields: `main_complaint`, `history_details`, vitals (`weight`, `height`, `bp`, `hr`, `temp`, `rr`, `spo2`), pregnancy info, past history.
- Lab fields: `malaria_rdt`, `blood_glucose`, urinalysis, cardiac markers.
- Doctor fields: `sys_cns`, `sys_cardio`, `working_diagnosis`, `treatment_plan`, `medication`, follow-ups.
- Workflow state: `state` (Selection: `nurse`, `doctor`, `lab`, `done`).
- Pharmacy order: `pharmacy_order_id` (Many2one → `med.pharmacy.order`)
- Audit trail: `audit_ids` (One2many → `med.consultation.audit`)
- IPD link: `ipd_id` (Many2one → `med.ipd`)

**Workflow:**
- `nurse` → `doctor` → `lab` → `done`
- Methods enforce state restrictions and audit logging.

**Views:**
- **Form View:** Header buttons for workflow actions (`Send to Doctor`, `Send to Lab`, `Return to Doctor`, `Complete Consultation`, `Send to Pharmacy`), notebook with pages:
  - `History`
  - `Vitals`
  - `Lab/Side Room`
  - `Doctor Assessment`
  - `Previous Consultations`
  - `Audit Trail`
- **Tree View:** Displays patient name, file number, date, and state.

---

### 2.3 IPD Admission (`med.ipd`)
**Purpose:** Manage inpatient admissions.

**Fields:**
- `patient_id` (Many2one → `med.patient`)
- `consultation_id` (Many2one → `med.consultation`)
- `name` (Char, readonly) — Auto-generated reference.
- `admission_date`, `discharge_date` (Date)
- `room_number`, `bed_number` (Char)
- `state` (Selection: `draft`, `admitted`, `discharged`) — Workflow status.
- `reason`, `notes` (Text)

**Workflow Actions:**
- `action_admit` — Transition from `draft` to `admitted`.
- `action_discharge` — Transition from `admitted` to `discharged`.

**Views:**
- **Form View:** Patient info, admission details, notes, and workflow buttons.
- **Tree View:** Summary of admissions with patient info and state.
- **Kanban View:** Professional, clickable cards with:
  - Patient name
  - Admission date
  - Room and bed
  - Status badge (colored by state)
  - Fully responsive and mobile-friendly

---

## 3. UI/UX Enhancements
- Tree view row size reduced for compact display.
- Kanban cards styled professionally:
  - Status badges: `draft` (gray), `admitted` (green), `discharged` (blue)
  - Card body includes patient, admission date, room/bed
  - Fully clickable using `oe_kanban_global_click` and `o_kanban_record` classes
- IPD kanban retains original responsiveness after CSS styling.
- Form views structured for usability with clear sections.

---

## 4. Security & Permissions
- Access restricted by user groups:
  - `med_nurse`
  - `med_doctor`
  - `med_lab`
  - `med_admin`
- Audit trail records user actions and role.
- IPD nurse notes (`med.ipd.note`) require explicit group access.

---

## 5. Known Limitations
- IPD nurse note creation restricted to proper groups.
- Pharmacy lines automatically generated from consultation medication text; unmatched medications are ignored.
- Advanced CSS modifications must preserve required classes for clickability.

---

## 6. Next Planned Features
- Ward round tracking with `ward.round` model.
- Inline nurse note kanban for IPD.
- Alerts for critical IPD admissions.
- Responsive dashboard with admission stats by state.

---

## 7. Deployment Notes
- Compatible with Odoo 15.
- Requires module `mail` for messaging and `mail.thread` support.
- Recommended to refresh UI assets after updates for CSS changes to take effect:


## Key Features
- Automatic stock deduction on dispensing.
- Stock movement audit trail.
- Admin-only deletion and full control over pharmacy orders and stock movements.
- Locking rules to prevent modification of dispensed/paid orders.
- Total amount computation for pharmacy orders.
- Form and tree views optimized for usability.



*This document is a living artifact and will be updated continuously as the MediSite Clinic system evolves.*
