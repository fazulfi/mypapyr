# Track B Deliverable B2 — Accessibility & WCAG 2.2 AA: Web / Primary-Source Evidence File

- **Deliverable**: B2 (Accessibility and WCAG 2.2 AA research)
- **Research mode**: Web / primary-source evidence (read-only, anonymous)
- **Access date for ALL URLs below**: 2026-07-31
- **Evidence standard**: primary sources first (w3.org, webaim.org, developer.chrome.com, developer.mozilla.org, official tool docs). Secondary/supporting sources are explicitly marked. No fabrication; gaps and uncertainties are stated in Section 10.
- **Related files**: normative SC text extracted programmatically from the W3C WCAG 2.2 HTML (download of `https://www.w3.org/TR/WCAG22/`, 2026-07-31); raw downloads kept in temp, not in repo.

---

## 1. WCAG 2.2 — Status, Date, Complete Success Criteria List, New-in-2.2 Criteria

### 1.1 Status and date

**Claim**: WCAG 2.2 is a W3C Recommendation. It was first published as a Recommendation on **5 October 2023**; the current version served at `https://www.w3.org/TR/WCAG22/` is the **12 December 2024** revision (an updated Recommendation incorporating changes since the original publication).

**Evidence**:
- Page: "Web Content Accessibility Guidelines (WCAG) 2.2", W3C Recommendation (accessed 2026-07-31).
- URL: https://www.w3.org/TR/WCAG22/ — page metadata: `generatedSubtitle: "W3C Recommendation 12 December 2024"`, `publishISODate: "2024-12-12T00:00:00.000Z"`, and header block "This version: https://www.w3.org/TR/2024/REC-WCAG22-20241212/"; "Latest published version: https://www.w3.org/TR/WCAG22/".
- URL: https://www.w3.org/TR/2023/REC-WCAG22-20231005/ — original "W3C Recommendation 5 October 2023".
- The spec's own Change Log states: "This section shows substantive changes incorporated into WCAG 2.2 since WCAG 2.1, as well as changes made to 2.2 since its original publication on 05 October 2023." (Appendix A, Change Log, WCAG 2.2 page, accessed 2026-07-31.)

**Note**: The task brief said "W3C Recommendation, 5 October 2023". That date is correct for the original REC; be aware that the normative text currently served (and quoted in Section 2) is the 12 December 2024 revision.

**Related conformance fact** (Section 5.2.1 Conformance Level, quoted from the spec): "For Level AA conformance, the web page satisfies all the Level A and Level AA success criteria, or a Level AA conforming alternate version is provided."

### 1.2 Complete list of WCAG 2.2 success criteria, grouped by principle (all levels)

Source: Table of Contents and SC sections of https://www.w3.org/TR/WCAG22/ (accessed 2026-07-31). Level annotations verified programmatically from each SC's `conformance-level` marker. WCAG 2.2 has **86 success criteria** (4.1.1 Parsing was removed; see note). List is complete — every numbered SC in the spec:

**Principle 1 — Perceivable**

| # | Name | Level |
|---|---|---|
| 1.1.1 | Non-text Content | A |
| 1.2.1 | Audio-only and Video-only (Prerecorded) | A |
| 1.2.2 | Captions (Prerecorded) | A |
| 1.2.3 | Audio Description or Media Alternative (Prerecorded) | A |
| 1.2.4 | Captions (Live) | AA |
| 1.2.5 | Audio Description (Prerecorded) | AA |
| 1.2.6 | Sign Language (Prerecorded) | AAA |
| 1.2.7 | Extended Audio Description (Prerecorded) | AAA |
| 1.2.8 | Media Alternative (Prerecorded) | AAA |
| 1.2.9 | Audio-only (Live) | AAA |
| 1.3.1 | Info and Relationships | A |
| 1.3.2 | Meaningful Sequence | A |
| 1.3.3 | Sensory Characteristics | A |
| 1.3.4 | Orientation | AA |
| 1.3.5 | Identify Input Purpose | AA |
| 1.3.6 | Identify Purpose | AAA |
| 1.4.1 | Use of Color | A |
| 1.4.2 | Audio Control | A |
| 1.4.3 | Contrast (Minimum) | AA |
| 1.4.4 | Resize Text | AA |
| 1.4.5 | Images of Text | AA |
| 1.4.6 | Contrast (Enhanced) | AAA |
| 1.4.7 | Low or No Background Audio | AAA |
| 1.4.8 | Visual Presentation | AAA |
| 1.4.9 | Images of Text (No Exception) | AAA |
| 1.4.10 | Reflow | AA |
| 1.4.11 | Non-text Contrast | AA |
| 1.4.12 | Text Spacing | AA |
| 1.4.13 | Content on Hover or Focus | AA |

**Principle 2 — Operable**

| # | Name | Level |
|---|---|---|
| 2.1.1 | Keyboard | A |
| 2.1.2 | No Keyboard Trap | A |
| 2.1.3 | Keyboard (No Exception) | AAA |
| 2.1.4 | Character Key Shortcuts | A |
| 2.2.1 | Timing Adjustable | A |
| 2.2.2 | Pause, Stop, Hide | A |
| 2.2.3 | No Timing | AAA |
| 2.2.4 | Interruptions | AAA |
| 2.2.5 | Re-authenticating | AAA |
| 2.2.6 | Timeouts | AAA |
| 2.3.1 | Three Flashes or Below Threshold | A |
| 2.3.2 | Three Flashes | AAA |
| 2.3.3 | Animation from Interactions | AAA |
| 2.4.1 | Bypass Blocks | A |
| 2.4.2 | Page Titled | A |
| 2.4.3 | Focus Order | A |
| 2.4.4 | Link Purpose (In Context) | A |
| 2.4.5 | Multiple Ways | AA |
| 2.4.6 | Headings and Labels | AA |
| 2.4.7 | Focus Visible | AA |
| 2.4.8 | Location | AAA |
| 2.4.9 | Link Purpose (Link Only) | AAA |
| 2.4.10 | Section Headings | AAA |
| 2.4.11 | **Focus Not Obscured (Minimum)** | **AA** |
| 2.4.12 | **Focus Not Obscured (Enhanced)** | **AAA** |
| 2.4.13 | **Focus Appearance** | **AAA** |
| 2.5.1 | Pointer Gestures | A |
| 2.5.2 | Pointer Cancellation | A |
| 2.5.3 | Label in Name | A |
| 2.5.4 | Motion Actuation | A |
| 2.5.5 | Target Size (Enhanced) | AAA |
| 2.5.6 | Concurrent Input Mechanisms | AAA |
| 2.5.7 | **Dragging Movements** | **AA** |
| 2.5.8 | **Target Size (Minimum)** | **AA** |

**Principle 3 — Understandable**

| # | Name | Level |
|---|---|---|
| 3.1.1 | Language of Page | A |
| 3.1.2 | Language of Parts | AA |
| 3.1.3 | Unusual Words | AAA |
| 3.1.4 | Abbreviations | AAA |
| 3.1.5 | Reading Level | AAA |
| 3.1.6 | Pronunciation | AAA |
| 3.2.1 | On Focus | A |
| 3.2.2 | On Input | A |
| 3.2.3 | Consistent Navigation | AA |
| 3.2.4 | Consistent Identification | AA |
| 3.2.5 | Change on Request | AAA |
| 3.2.6 | **Consistent Help** | **A** |
| 3.3.1 | Error Identification | A |
| 3.3.2 | Labels or Instructions | A |
| 3.3.3 | Error Suggestion | AA |
| 3.3.4 | Error Prevention (Legal, Financial, Data) | AA |
| 3.3.5 | Help | AAA |
| 3.3.6 | Error Prevention (All) | AAA |
| 3.3.7 | **Redundant Entry** | **A** |
| 3.3.8 | **Accessible Authentication (Minimum)** | **AA** |
| 3.3.9 | **Accessible Authentication (Enhanced)** | **AAA** |

**Principle 4 — Robust**

| # | Name | Level |
|---|---|---|
| 4.1.2 | Name, Role, Value | A |
| 4.1.3 | Status Messages | AA |

**Note on 4.1.1**: The spec still contains the section "Success Criterion 4.1.1 Parsing (Obsolete and removed)" stating: "This criterion was originally adopted to address problems that assistive technology had directly parsing HTML. Assistive technology no longer has any need to directly parse HTML. Consequently, these problems either no longer exist or are addressed by other criteria. This criterion no longer has utility and is removed." (WCAG 2.2, accessed 2026-07-31.) It does not count toward conformance.

### 1.3 Criteria NEW in WCAG 2.2 (from the spec's "New Features in WCAG 2.2" section)

**Claim**: WCAG 2.2 adds **9** new success criteria, not 7. The spec's "New Features in WCAG 2.2" section names: "2.4.11 Focus Not Obscured (Minimum) (AA) 2.4.12 Focus Not Obscured (Enhanced) (AAA) 2.4.13 Focus Appearance (AAA) 2.5.7 Dragging Movements (AA) 2.5.8 Target Size (Minimum) (AA) 3.2.6 Consistent Help (A) 3.3.7 Redundant Entry (A) 3.3.8 Accessible Authentication (Minimum) (AA) 3.3.9 Accessible Authentication (Enhanced) (AAA)".

**Evidence**: Section "New Features in WCAG 2.2", https://www.w3.org/TR/WCAG22/ (accessed 2026-07-31). It also states: "WCAG 2.2 extends WCAG 2.1 by adding new success criteria… This additive approach helps to make it clear that sites which conform to WCAG 2.2 also conform to WCAG 2.1."

**Correction vs. task brief**: The task brief listed 7 criteria (2.4.11, 2.4.12, 2.5.7, 2.5.8, 3.2.6, 3.3.7, 3.3.8). The spec additionally lists **2.4.13 Focus Appearance (AAA)** and **3.3.9 Accessible Authentication (Enhanced) (AAA)**. For a WCAG 2.2 AA target, the new AA-level criteria that apply are: **2.4.11, 2.5.7, 2.5.8, 3.3.8** (and the two new Level A criteria 3.2.6, 3.3.7, since AA includes all A). Level of each new SC confirmed by per-criterion `conformance-level` markers in the spec HTML.

**Understanding/Quickref URLs** (verified 200, accessed 2026-07-31):
- Understanding index: https://www.w3.org/WAI/WCAG22/Understanding/
- How to Meet (Quickref): https://www.w3.org/WAI/WCAG22/quickref/
- Per-criterion Understanding pages follow the pattern https://www.w3.org/WAI/WCAG22/Understanding/<slug>.html (e.g., `dragging-movements.html`, `target-size-minimum.html`, `focus-not-obscured-minimum.html`, `consistent-help.html`, `redundant-entry.html`, `accessible-authentication-minimum.html`).

---

## 2. Success Criteria Most Relevant to a File-Conversion Web App — Exact Normative Text (quoted from WCAG 2.2)

All quotes below are **verbatim** from the normative SC sections of https://www.w3.org/TR/WCAG22/ (12 December 2024 revision, accessed 2026-07-31). Understanding-page links given per SC.

### 1.1.1 Non-text Content — Level A
> All non-text content that is presented to the user has a text alternative that serves the equivalent purpose, except for the situations listed below.
> - **Controls, Input**: If non-text content is a control or accepts user input, then it has a name that describes its purpose. (Refer to Success Criterion 4.1.2…)
> - **Time-Based Media**: If non-text content is time-based media, then text alternatives at least provide descriptive identification of the non-text content. (Refer to Guideline 1.2…)
> - **Test**: If non-text content is a test or exercise that would be invalid if presented in text, then text alternatives at least provide descriptive identification of the non-text content.
> - **Sensory**: If non-text content is primarily intended to create a specific sensory experience, then text alternatives at least provide descriptive identification of the non-text content.
> - **CAPTCHA**: If the purpose of non-text content is to confirm that content is being accessed by a person rather than a computer, then text alternatives that identify and describe the purpose of the non-text content are provided, and alternative forms of CAPTCHA using output modes for different types of sensory perception are provided to accommodate different disabilities.
> - **Decoration, Formatting, Invisible**: If non-text content is pure decoration, is used only for visual formatting, or is not presented to users, then it is implemented in a way that it can be ignored by assistive technology.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/non-text-content.html

### 1.3.1 Info and Relationships — Level A
> Information, structure, and relationships conveyed through presentation can be programmatically determined or are available in text.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/info-and-relationships.html

### 1.3.2 Meaningful Sequence — Level A
> When the sequence in which content is presented affects its meaning, a correct reading sequence can be programmatically determined.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/meaningful-sequence.html

### 1.4.3 Contrast (Minimum) — Level AA
> The visual presentation of text and images of text has a contrast ratio of at least 4.5:1, except for the following:
> - **Large Text**: Large-scale text and images of large-scale text have a contrast ratio of at least 3:1;
> - **Incidental**: Text or images of text that are part of an inactive user interface component, that are pure decoration, that are not visible to anyone, or that are part of a picture that contains significant other visual content, have no contrast requirement.
> - **Logotypes**: Text that is part of a logo or brand name has no contrast requirement.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html

### 1.4.4 Resize Text — Level AA
> Except for captions and images of text, text can be resized without assistive technology up to 200 percent without loss of content or functionality.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html

### 1.4.10 Reflow — Level AA
> Content can be presented without loss of information or functionality, and without requiring scrolling in two dimensions for:
> - Vertical scrolling content at a width equivalent to 320 CSS pixels;
> - Horizontal scrolling content at a height equivalent to 256 CSS pixels.
> Except for parts of the content which require two-dimensional layout for usage or meaning.
> Note 1: 320 CSS pixels is equivalent to a starting viewport width of 1280 CSS pixels wide at 400% zoom…
> Note 2: Examples of content which requires two-dimensional layout are images required for understanding (such as maps and diagrams), video, games, presentations, data tables (not individual cells), and interfaces where it is necessary to keep toolbars in view while manipulating content.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/reflow.html

### 1.4.11 Non-text Contrast — Level AA
> The visual presentation of the following have a contrast ratio of at least 3:1 against adjacent color(s):
> - **User Interface Components**: Visual information required to identify user interface components and states, except for inactive components or where the appearance of the component is determined by the user agent and not modified by the author;
> - **Graphical Objects**: Parts of graphics required to understand the content, except when a particular presentation of graphics is essential to the information being conveyed.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html

### 1.4.12 Text Spacing — Level AA
> In content implemented using markup languages that support the following text style properties, no loss of content or functionality occurs by setting all of the following and by changing no other style property:
> - Line height (line spacing) to at least 1.5 times the font size;
> - Spacing following paragraphs to at least 2 times the font size;
> - Letter spacing (tracking) to at least 0.12 times the font size;
> - Word spacing to at least 0.16 times the font size.
> Exception: Human languages and scripts that do not make use of one or more of these text style properties in written text can conform using only the properties that exist for that combination of language and script.
> Note 1: Content is not required to use these text spacing values. The requirement is to ensure that when a user overrides the authored text spacing, content or functionality is not lost.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html

### 2.1.1 Keyboard — Level A
> All functionality of the content is operable through a keyboard interface without requiring specific timings for individual keystrokes, except where the underlying function requires input that depends on the path of the user's movement and not just the endpoints.
> Note 1: This exception relates to the underlying function, not the input technique…
> Note 2: This does not forbid and should not discourage providing mouse input or other input methods in addition to keyboard operation.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html

### 2.1.2 No Keyboard Trap — Level A
> If keyboard focus can be moved to a component of the page using a keyboard interface, then focus can be moved away from that component using only a keyboard interface, and, if it requires more than unmodified arrow or tab keys or other standard exit methods, the user is advised of the method for moving focus away.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/no-keyboard-trap.html

### 2.2.1 Timing Adjustable — Level A
> For each time limit that is set by the content, at least one of the following is true:
> - **Turn off**: The user is allowed to turn off the time limit before encountering it; or
> - **Adjust**: The user is allowed to adjust the time limit before encountering it over a wide range that is at least ten times the length of the default setting; or
> - **Extend**: The user is warned before time expires and given at least 20 seconds to extend the time limit with a simple action (for example, "press the space bar"), and the user is allowed to extend the time limit at least ten times; or
> - **Real-time Exception**: The time limit is a required part of a real-time event (for example, an auction), and no alternative to the time limit is possible; or
> - **Essential Exception**: The time limit is essential and extending it would invalidate the activity; or
> - **20 Hour Exception**: The time limit is longer than 20 hours.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/timing-adjustable.html

### 2.2.2 Pause, Stop, Hide — Level A
> For moving, blinking, scrolling, or auto-updating information, all of the following are true:
> - **Moving, blinking, scrolling**: For any moving, blinking or scrolling information that (1) starts automatically, (2) lasts more than five seconds, and (3) is presented in parallel with other content, there is a mechanism for the user to pause, stop, or hide it unless the movement, blinking, or scrolling is part of an activity where it is essential; and
> - **Auto-updating**: For any auto-updating information that (1) starts automatically and (2) is presented in parallel with other content, there is a mechanism for the user to pause, stop, or hide it or to control the frequency of the update unless the auto-updating is part of an activity where it is essential.
> Note 4: An animation that occurs as part of a preload phase or similar situation can be considered essential if interaction cannot occur during that phase for all users and if not indicating progress could confuse users or cause them to think that content was frozen or broken.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html

### 2.4.1 Bypass Blocks — Level A
> A mechanism is available to bypass blocks of content that are repeated on multiple web pages.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/bypass-blocks.html

### 2.4.3 Focus Order — Level A
> If a web page can be navigated sequentially and the navigation sequences affect meaning or operation, focusable components receive focus in an order that preserves meaning and operability.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/focus-order.html

### 2.4.4 Link Purpose (In Context) — Level A
> The purpose of each link can be determined from the link text alone or from the link text together with its programmatically determined link context, except where the purpose of the link would be ambiguous to users in general.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/link-purpose-in-context.html

### 2.4.6 Headings and Labels — Level AA
> Headings and labels describe topic or purpose.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/headings-and-labels.html

### 2.4.7 Focus Visible — Level AA
> Any keyboard operable user interface has a mode of operation where the keyboard focus indicator is visible.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html

### 2.4.11 Focus Not Obscured (Minimum) — Level AA — **NEW in 2.2**
> When a user interface component receives keyboard focus, the component is not entirely hidden due to author-created content.
> Note 1: Where content in a configurable interface can be repositioned by the user, then only the initial positions of user-movable content are considered for testing and conformance of this success criterion.
> Note 2: Content opened by the user may obscure the component receiving focus. If the user can reveal the focused component without advancing the keyboard focus, the component with focus is not considered visually hidden due to author-created content.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html

### 2.5.7 Dragging Movements — Level AA — **NEW in 2.2**
> All functionality that uses a dragging movement for operation can be achieved by a single pointer without dragging, unless dragging is essential or the functionality is determined by the user agent and not modified by the author.
> Note: This requirement applies to web content that interprets pointer actions (i.e., this does not apply to actions that are required to operate the user agent or assistive technology).

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html

### 2.5.8 Target Size (Minimum) — Level AA — **NEW in 2.2**
> The size of the target for pointer inputs is at least 24 by 24 CSS pixels, except when:
> - **Spacing**: Undersized targets (those less than 24 by 24 CSS pixels) are positioned so that if a 24 CSS pixel diameter circle is centered on the bounding box of each, the circles do not intersect another target or the circle for another undersized target;
> - **Equivalent**: The function can be achieved through a different control on the same page that meets this criterion;
> - **Inline**: The target is in a sentence or its size is otherwise constrained by the line-height of non-target text;
> - **User Agent Control**: The size of the target is determined by the user agent and is not modified by the author;
> - **Essential**: A particular presentation of the target is essential or is legally required for the information being conveyed.
> Note 1: Targets that allow for values to be selected spatially based on position within the target are considered one target… Examples include sliders, color pickers displaying a gradient of colors, or editable areas where you position the cursor.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html

### 3.1.1 Language of Page — Level A
> The default human language of each web page can be programmatically determined.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/language-of-page.html

### 3.1.2 Language of Parts — Level AA
> The human language of each passage or phrase in the content can be programmatically determined except for proper names, technical terms, words of indeterminate language, and words or phrases that have become part of the vernacular of the immediately surrounding text.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/language-of-parts.html

### 3.2.3 Consistent Navigation — Level AA
> Navigational mechanisms that are repeated on multiple web pages within a set of web pages occur in the same relative order each time they are repeated, unless a change is initiated by the user.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/consistent-navigation.html

### 3.2.4 Consistent Identification — Level AA
> Components that have the same functionality within a set of web pages are identified consistently.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/consistent-identification.html

### 3.2.6 Consistent Help — Level A — **NEW in 2.2**
> If a web page contains any of the following help mechanisms, and those mechanisms are repeated on multiple web pages within a set of web pages, they occur in the same order relative to other page content, unless a change is initiated by the user:
> - Human contact details;
> - Human contact mechanism;
> - Self-help option;
> - A fully automated contact mechanism.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/consistent-help.html

### 3.3.1 Error Identification — Level A
> If an input error is automatically detected, the item that is in error is identified and the error is described to the user in text.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html

### 3.3.2 Labels or Instructions — Level A
> Labels or instructions are provided when content requires user input.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html

### 3.3.3 Error Suggestion — Level AA
> If an input error is automatically detected and suggestions for correction are known, then the suggestions are provided to the user, unless it would jeopardize the security or purpose of the content.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/error-suggestion.html

### 3.3.4 Error Prevention (Legal, Financial, Data) — Level AA
> For web pages that cause legal commitments or financial transactions for the user to occur, that modify or delete user-controllable data in data storage systems, or that submit user test responses, at least one of the following is true:
> - **Reversible**: Submissions are reversible.
> - **Checked**: Data entered by the user is checked for input errors and the user is provided an opportunity to correct them.
> - **Confirmed**: A mechanism is available for reviewing, confirming, and correcting information before finalizing the submission.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/error-prevention-legal-financial-data.html

### 3.3.7 Redundant Entry — Level A — **NEW in 2.2**
> Information previously entered by or provided to the user that is required to be entered again in the same process is either:
> - auto-populated, or
> - available for the user to select.
> Except when:
> - re-entering the information is essential,
> - the information is required to ensure the security of the content, or
> - previously entered information is no longer valid.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/redundant-entry.html

### 3.3.8 Accessible Authentication (Minimum) — Level AA — **NEW in 2.2**
> A cognitive function test (such as remembering a password or solving a puzzle) is not required for any step in an authentication process unless that step provides at least one of the following:
> - **Alternative**: Another authentication method that does not rely on a cognitive function test.
> - **Mechanism**: A mechanism is available to assist the user in completing the cognitive function test.
> - **Object Recognition**: The cognitive function test is to recognize objects.
> - **Personal Content**: The cognitive function test is to identify non-text content the user provided to the website.
> Note 2: Examples of mechanisms that satisfy this criterion include: support for password entry by password managers to reduce memory need, and copy and paste to reduce the cognitive burden of re-typing.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html

### 4.1.2 Name, Role, Value — Level A
> For all user interface components (including but not limited to: form elements, links and components generated by scripts), the name and role can be programmatically determined; states, properties, and values that can be set by the user can be programmatically set; and notification of changes to these items is available to user agents, including assistive technologies.
> Note: This success criterion is primarily for web authors who develop or script their own user interface components. For example, standard HTML controls already meet this success criterion when used according to specification.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html

### 4.1.3 Status Messages — Level AA
> In content implemented using markup languages, status messages can be programmatically determined through role or properties such that they can be presented to the user by assistive technologies without receiving focus.

Understanding: https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html

---

## 3. WAI-ARIA 1.2 — Status, Roles, and APG Patterns

### 3.1 Status/date
**Claim**: WAI-ARIA 1.2 is a W3C Recommendation published **06 June 2023**.
**Evidence**: "Accessible Rich Internet Applications (WAI-ARIA) 1.2", https://www.w3.org/TR/wai-aria-1.2/ — page metadata `generatedSubtitle: "W3C Recommendation 06 June 2023"`, `publishISODate: "2023-06-06T00:00:00.000Z"`; "This version: https://www.w3.org/TR/2023/REC-wai-aria-1.2-20230606/". (Accessed 2026-07-31.)

### 3.2 Role definitions relevant to file upload / dialogs / progress / status / tabs (quoted from the ARIA 1.2 spec)
Source: role definition sections of https://www.w3.org/TR/wai-aria-1.2/ (accessed 2026-07-31).

- **dialog**: "A dialog is a descendant window of the primary window of a web application. For HTML pages, the primary application window is the entire web document, i.e., the body element."
- **alertdialog**: "A type of dialog that contains an alert message, where initial focus goes to an element within the dialog. See related alert and dialog."
- **progressbar**: "An element that displays the progress status for tasks that take a long time."
- **status**: "A type of live region whose content is advisory information for the user but is not important enough to justify an alert, often but not necessarily presented as a status bar."
- **alert**: "A type of live region with important, and usually time-sensitive, information. See related alertdialog and status."
- **tab**: "A grouping label providing a mechanism for selecting the tab content that is to be rendered to the user."

### 3.3 ARIA Authoring Practices Guide (APG) — current URL structure (verified 2026-07-31)
**Note on URLs**: The APG was restructured; the old `/patterns/dialog/` and `/patterns/progressbar/` URLs return 404. Current pattern URLs verified live:
- Patterns index: https://www.w3.org/WAI/ARIA/apg/patterns/ (lists 30 patterns)
- Dialog (Modal): https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/
- Alert: https://www.w3.org/WAI/ARIA/apg/patterns/alert/
- Alert and Message Dialogs: https://www.w3.org/WAI/ARIA/apg/patterns/alertdialog/
- Tabs: https://www.w3.org/WAI/ARIA/apg/patterns/tabs/

### 3.4 APG Dialog (Modal) pattern — key normative guidance (quoted)
Source: "Dialog (Modal) Pattern", https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/ (accessed 2026-07-31):

> "A dialog is a window overlaid on either the primary window or another dialog window. Windows under a modal dialog are inert. That is, users cannot interact with content outside an active dialog window."
> - Keyboard interaction: "When a dialog opens, focus moves to an element inside the dialog." "Tab: Moves focus to the next tabbable element inside the dialog… If focus is on the last tabbable element inside the dialog, moves focus to the first tabbable element inside the dialog." "Shift + Tab: …moves focus to the previous tabbable element…". "Escape: Closes the dialog."
> - "When a dialog closes, focus returns to the element that invoked the dialog unless…" (invoker no longer exists, or workflow conditions justify different placement).
> - Initial focus: "Generally, focus is initially set on the first focusable element." For content with semantic structure: "it is advisable to add `tabindex="-1"` to a static element at the start of the content and initially focus that element." For final-step/not-easily-reversible processes (e.g., deleting data): "it may be advisable to set focus on the least destructive action."
> - "It is strongly recommended that the tab sequence of all dialogs include a visible element with role `button` that closes the dialog, such as a close icon or cancel button."
> - Roles/states: container has `role="dialog"`; all operable elements are descendants; `aria-modal="true"`; accessible name via `aria-labelledby` (visible title) or `aria-label`; optional `aria-describedby`.
> - "Because marking a dialog modal by setting aria-modal to `true` can prevent users of some assistive technologies from perceiving content outside the dialog… mark a dialog modal **only when both:** 1. Application code prevents all users from interacting in any way with content outside of it. 2. Visual styling obscures the content outside of it." (Legacy note on `aria-hidden` usage for inert layers.)

### 3.5 APG Tabs pattern — key guidance (quoted)
Source: "Tabs Pattern", https://www.w3.org/WAI/ARIA/apg/patterns/tabs/ (accessed 2026-07-31):
- Keyboard: "Tab: When focus moves into the tab list, places focus on the active `tab` element." "Left Arrow / Right Arrow: moves focus to the previous/next tab… Optionally, activates the newly focused tab." "Space or Enter: Activates the tab if it was not activated automatically on focus."
- Roles/states: container `role="tablist"`, each tab `role="tab"`, panels `role="tabpanel"`; `aria-labelledby` on tablist (or `aria-label`); each tab has `aria-controls` referencing its panel; active tab has `aria-selected="true"`, others `false`; each tabpanel has `aria-labelledby` referencing its tab; optional `aria-orientation="vertical"`.
- "When the tabpanel does not contain any focusable elements or the first element with content is not focusable, the tabpanel should set `tabindex="0"`."

### 3.6 APG Alert pattern — key guidance (quoted)
Source: "Alert Pattern", https://www.w3.org/WAI/ARIA/apg/patterns/alert/ (accessed 2026-07-31):
- "An alert is an element that displays a brief, important message in a way that attracts the user's attention without interrupting the user's task. Dynamically rendered alerts are automatically announced by most screen readers… screen readers do not inform users of alerts that are present on the page before page load completes."
- "It is crucial they do not affect keyboard focus." "It is also important to avoid designing alerts that disappear automatically." Roles: "The widget has a role of alert." Keyboard interaction: "Not applicable."

### 3.7 Progressbar pattern status — **removed from current APG** (verified 2026-07-31)
**Claim**: The current APG patterns index no longer includes a Progressbar pattern (the old URL `/WAI/ARIA/apg/patterns/progressbar/` returns 404). The `progressbar` role remains normative in ARIA 1.2 (Section 3.2 above), and MDN documents `progressbar` as a role with implicit live-region behavior (see Section 7.2). For implementation guidance, the HTML native `<progress>` element and `aria-valuemin`/`aria-valuenow`/`aria-valuemax` pattern per MDN are the current primary references.
**Evidence**: APG Patterns index https://www.w3.org/WAI/ARIA/apg/patterns/ fetched 2026-07-31; grep of the downloaded index for "progressbar" → 0 matches; HTTP status for https://www.w3.org/WAI/ARIA/apg/patterns/progressbar/ → 404.

---

## 4. Automated Accessibility Testing Tools — Documented Coverage and Limitations

### 4.1 axe-core (Deque)
- **Current version**: **4.12.1**, released 2026-06-09/10 (tag v4.12.1, "Latest" on releases page; release notes state "This release does not impact axe results."). Previous: 4.12.0 (2026-06-01) added the `aria-tab-name` rule, deprecated `landmark-complementary-is-top-level`, and other fixes for `target-size`, `scrollable-region-focusable`. Sources: https://github.com/dequelabs/axe-core/releases and https://github.com/dequelabs/axe-core/blob/master/CHANGELOG.md (accessed 2026-07-31).
- **Documented coverage**: README (https://github.com/dequelabs/axe-core/blob/develop/README.md, accessed 2026-07-31): "Axe-core has different types of rules, for WCAG 2.0, 2.1, 2.2 on level A, AA and AAA as well as a number of best practices…"
- **Documented limitation (verbatim)**: "With axe-core, you can find **on average 57% of WCAG issues automatically**. Additionally, axe-core will return elements as 'incomplete' where axe-core could not be certain, and manual review is needed." (axe-core README.)
- **Rule inventory** (doc/rule-descriptions.md, generated for axe 4.12, accessed 2026-07-31 via raw.githubusercontent.com/dequelabs/axe-core/develop/doc/rule-descriptions.md): rules grouped as WCAG 2.0 A&AA, WCAG 2.1 A&AA, **WCAG 2.2 A&AA** (currently only `target-size` — "These rules are disabled by default, until WCAG 2.2 is more widely adopted and required."), Best Practices, WCAG 2.x AAA, Experimental, Deprecated. Each rule carries tags mapping to SCs (e.g., `wcag143`, `wcag258`, `wcag412`) and many map to W3C ACT Rules.

### 4.2 axe DevTools (Deque)
- Source: https://www.deque.com/axe/devtools/ (accessed 2026-07-31).
- Marketing-documented coverage: "Fast, accurate, automated, intelligent accessibility testing tools…"; "zero false positives" commitment; "The Axe DevTools Extension has been installed 800,000+ times in Chrome"; "axe-core, invented by Deque, has been downloaded 4 Billion+ times."
- **Documented limitation (FAQ, verbatim)**: "Do automated accessibility testing tools replace manual accessibility testing? No, automated testing complements manual testing. Automated accessibility testing tools enable testers to quickly identify a high percentage of issues—**up to 80% with Deque's tools**. Manual testing can then be used to focus on more complex issues that automation alone can't detect."
- "Does Axe DevTools replace screen reader (JAWS, NVDA, TalkBack, and VoiceOver) testing? No. While automated and semi-automated tests can eliminate a large percentage of issues… manual testing with screen readers is sometimes still required to be completely certain…"
- vs Lighthouse: "Lighthouse is a more general tool, whereas Axe DevTools is more comprehensive and purpose-built for accessibility. Google Lighthouse has actually run on Deque's open-source accessibility library, Axe-core, since 2017, but does not run the full set of over 70 tests that Axe DevTools does."

### 4.3 Lighthouse accessibility audits (Chrome)
- Source: "Lighthouse accessibility score", https://developer.chrome.com/docs/lighthouse/accessibility/ (accessed 2026-07-31; page "Last updated 2025-10-22 UTC").
- "The Lighthouse Accessibility score is a weighted average of all accessibility audits. **Weighting is based on axe user impact assessments.**"
- "Each accessibility audit is pass or fail. Unlike the Performance audits, a page doesn't get points for partially passing an accessibility audit."
- Publishes the full audit list with weights (e.g., `button, link, and menuitem elements have accessible names` 7; `Elements with role="dialog" or role="alertdialog" have accessible names` 7; **`ARIA progressbar elements have accessible names` 7**; `Background and foreground colors have a sufficient contrast ratio` 7; `Image elements have [alt] attributes` 10; `Form elements have associated labels` 10; `<html> element has a [lang] attribute` 7; etc.).
- **Manual checks** (must be done by a human; not scored): "Custom controls have ARIA roles", "Custom controls have associated labels", "**Trapped user focus**", "**Interactive controls are keyboard-focusable**", "Interactive elements indicate their purpose and state", "**The page has a logical tab order**", "**The user's focus is directed to new content added to the page**", "Offscreen content is hidden from assistive technology", "HTML5 landmark elements are used to improve navigation", "Visual order on the page follows DOM order".

### 4.4 WAVE (WebAIM)
- Sources: https://wave.webaim.org/ and https://wave.webaim.org/help (both accessed 2026-07-31; no version number published on these pages).
- "WAVE is suite of tools designed to help you make your web content more accessible."
- **Documented limitations (verbatim)**: "**WAVE cannot tell you if your web content is accessible. Only a human can determine true accessibility.**" "**The absence of errors DOES NOT mean your page is accessible or compliant.**" "WAVE cannot check all of the issues in these guidelines - **no automated tool can**." "we never indicate that your page is accessible or if it has 'passed' WAVE."
- Standards coverage: "We have added numerous tests for accessibility, including many checks for compliance issues found in the Section 508 and **WCAG 2.2** guidelines." (WAVE help page.)
- Architecture differences: "The online version of WAVE has limitations in applying some scripting. The extension and WAVE API provide more complete scripting support." The browser extensions (Chrome/Firefox/Edge) "evaluate content as it is rendered within your web browser… private, intranet, password protected, dynamically generated, or scripted web content."
- Hidden content: "WAVE detects accessibility issues in all page elements, even those that are hidden using CSS, the hidden attribute, aria-hidden="true", and/or tabindex="-1". This is by design." (Can produce errors in intentionally-hidden content; can be ignored when never presented.)

### 4.5 HTML CodeSniffer (Squiz Labs)
- Source: https://squizlabs.github.io/HTML_CodeSniffer/ (accessed 2026-07-31).
- "HTML_CodeSniffer is a client-side script that checks HTML source code and detects violations of a defined coding standard. HTML_CodeSniffer is written entirely in JavaScript, **does not require any server-side processing** and can be extended…"
- Standards: "HTML_CodeSniffer comes with standards that enforce the three conformance levels of the Web Content Accessibility Guidelines (**WCAG 2.1**), and the web-related components of the U.S. 'Section 508' legislation." Auditor interface via bookmarklet.
- **Limitation note**: The project page documents WCAG 2.1 only (not WCAG 2.2), and the bookmarklet is described for Chrome, Firefox, Safari, Internet Explorer. No current version number is stated on the page.

### 4.6 Summary: what automation can and cannot catch (with documented evidence)
- Automation catches: name/role/value issues, ARIA attribute validity, labels, alt text presence, contrast ratios, lang attributes, duplicate IDs, target size (axe `target-size`), certain keyboard-focusable structure checks, and (in Lighthouse's manual list) some focus checks remain human.
- Automation cannot (documented): judge equivalence of alt text or meaning (WAVE), confirm true accessibility (WAVE), find every WCAG issue (axe-core README's 57% figure; WAVE's "no automated tool can"), replace screen reader testing (Deque FAQ), and many focus-management/tab-order/dialog-trapping checks are only partially automatable (Lighthouse lists "Trapped user focus", "logical tab order", "focus directed to new content" as **manual** checks).
- Human/manual testing is therefore required; see Section 5.

---

## 5. Manual / Screen-Reader Testing Standards

### 5.1 WAI evaluation resources
- "Easy Checks – A First Review of Web Accessibility", https://www.w3.org/WAI/test-evaluate/easy-checks/ (accessed 2026-07-31; page footer: "Updated: 21 March 2024"; editors Kevin White, Andrew Arch, Shawn Lawton Henry). Disclaimer (verbatim): "These checks cover just a few accessibility issues and are designed to be quick and easy, rather than exhaustive. A web page could seem to pass these checks, yet still have significant accessibility barriers."
  - Checks covered: Image Alternative Text; Page Title; Headings; Color Contrast; Skip Link; Visible Keyboard Focus; Language of Page; Zoom; Captions; Transcripts; Audio Description; Form Field Labels; Required Fields.
  - The page's "Keyboard access and visual focus" guidance includes checking: Tab order ("follows the logical reading order"), Visual focus ("you can tell which element has focus"), all functionality by keyboard, and that "some functionality is available only with mouse hover, and is not available with keyboard focus" is a common problem.
- **"Keyboard Testing" standalone WAI page: NOT FOUND.** The URL commonly cited for WAI "Keyboard Testing" (https://www.w3.org/WAI/test-evaluate/keyboard/) returns 404 as of 2026-07-31. Closest W3C primary sources: Easy Checks keyboard section (above), the Evaluating Web Accessibility overview (https://www.w3.org/WAI/test-evaluate/), and Understanding 2.1.1/2.1.2. WebAIM's keyboard techniques (Section 5.3) is the most complete freely documented keyboard-testing procedure found.
- W3C "no tool alone" statement (Evaluating Web Accessibility overview, https://www.w3.org/WAI/test-evaluate/, accessed 2026-07-31): "There are evaluation tools that help with evaluation. However, **no tool alone can determine if a site meets accessibility standards. Knowledgeable human evaluation is required** to determine if a site is accessible."

### 5.2 Screen reader market share — WebAIM Screen Reader User Survey #10 (latest)
- Page: "WebAIM: Screen Reader User Survey #10 Results", https://webaim.org/projects/screenreadersurvey10/ (accessed 2026-07-31).
- Survey period: "In December 2023 and January 2024, WebAIM surveyed preferences of screen reader users. We received **1539 valid responses**." This is the 10th survey (follow-up to 9 previous between January 2009 and June 2021). As of access date, this remains the latest published survey; no newer edition was found.
- Primary desktop/laptop screen reader: **JAWS 40.5%** (619), **NVDA 37.7%** (577), **VoiceOver 9.7%** (148), Dolphin SuperNova 3.7%, ZoomText/Fusion 2.7%, Orca 2.4%, Narrator 0.7%, Other 2.7%.
- Commonly used (any use): **NVDA 65.6%**, **JAWS 60.5%**, VoiceOver 43.9%, Narrator 37.3%, Orca 8.3%.
- Regional variance: JAWS > NVDA in North America (55.5% vs 24.0%) and Australia; NVDA > JAWS in Europe (37.2% vs 29.7%), Africa/Middle East (69.9% vs 23.3%), Asia (70.8% vs 22.9%).
- Browsers with primary SR: Chrome 52.3%, Edge 19.3%, Firefox 16.0%, Safari 8.0%. Top combos: JAWS+Chrome 24.7%, NVDA+Chrome 21.3%, JAWS+Edge 11.4%, NVDA+Firefox 10.0%.
- Mobile: 91.3% use a screen reader on a mobile device; primary mobile platform iOS 70.6% vs Android 27.6%; **mobile screen readers commonly used: VoiceOver 70.6%, TalkBack 34.7%**.
- OS: Windows 86.1%, Mac 9.6%, Linux 2.9%.
- **Most problematic items (in order)**: 1. CAPTCHA; 2. **Interactive elements like menus, tabs, and dialogs do not behave as expected**; 3. Links or buttons that do not make sense; 4. **Screens or parts of screens that change unexpectedly**; 5. **Lack of keyboard accessibility**; 6. Images with missing or improper descriptions; 7. **Complex or difficult forms**; 8. Missing or improper headings; 9. Too many links/navigation; 10. Complex data tables; 11. Inaccessible or missing search; 12. Lack of "skip to main content" links.
- Navigation on long pages: 71.6% navigate via headings first.

### 5.3 Screen readers and documented testing workflows
- **NVDA (Windows, free)** — WebAIM: "Using NVDA to Evaluate Web Accessibility", https://webaim.org/articles/nvda/ (accessed 2026-07-31). Workflow: download free, launch with Ctrl+Alt+N, configure speech/braille settings, test reading (NVDA+Down), navigation by element keys (H headings, D landmarks, F form controls, T tables, B buttons, K links, G graphics, L lists, I list items; Shift reverses), forms in Focus mode vs Browse mode (NVDA+Space toggles), Elements List NVDA+F7, Screen Curtain/braille options, practice tasks without a monitor.
- **JAWS (Windows, paid)** — WebAIM: "Using JAWS to Evaluate Web Accessibility", https://webaim.org/articles/jaws/ (accessed 2026-07-31). Workflow: open JAWS before browser; quick keys H/1-6/R/F/T/B/G/L/I; Virtual Cursor vs Forms Mode (JAWS+Z toggles); lists via Ctrl+JAWS+key; JAWS+F7 links list, JAWS+F6 headings list, JAWS+F5 form elements; practice without monitor.
- **VoiceOver (macOS/iOS, built-in)** — WebAIM: "Using VoiceOver to Evaluate Web Accessibility", https://webaim.org/articles/voiceover/ (accessed 2026-07-31). Workflow: start with Command+F5 (or TouchID triple-click on newer Macs); VO key = Control+Option; read (VO+A), navigate by rotor (VO+U; Headers, Links, Form controls, Tables, etc.); "VoiceOver currently functions best with the Safari web browser"; enable full keyboard access; **Screen Curtain with VO+Shift+F11** to test audio-only; mobile version touch-based.
- **TalkBack (Android, built-in)** — Google Android Developers, "Test your app's accessibility", https://developer.android.com/guide/topics/ui/accessibility/testing (accessed 2026-07-31; page updated 2026-04-16). Workflow: enable TalkBack (Settings → Accessibility → TalkBack); swipe through elements in sequence; check "Does the spoken feedback for each element convey its content or purpose?" and whether announcements are succinct; enable TalkBack developer settings (log output VERBOSE; display speech output on screen) for easier testing.
- **Keyboard-only testing** — WebAIM: "Keyboard Accessibility", https://webaim.org/techniques/keyboard/ (accessed 2026-07-31). Includes: focus indicators must be visible; logical navigation order; don't use tabindex ≥ 1; keyboard traps (Esc should release focus; modal dialogs/ARIA menus); and a **keyboard testing table** of standard keystrokes per interaction (Tab/Shift+Tab navigation, Enter for links, Enter/Space for buttons, Space for checkboxes, arrows for radios/selects, Esc for dialogs, arrows/Home/End for sliders, arrows for tab panels, etc.). Also: "Be sure to test keyboard accessibility on mobile devices—users with disabilities often utilize an external keyboard with phones and tablets."

---

## 6. File Upload Accessibility Guidance

### 6.1 WAI Forms tutorial — "File Uploads" page does NOT exist (verified)
**Claim**: The WAI Web Accessibility Tutorials "Forms" section has **no page titled "File Uploads"**. The task brief referenced "WAI tutorial 'Forms — File Uploads'"; that specific page is not published. The Forms tutorial covers: Labeling Controls, Grouping Controls, Form Instructions, Validating Input, User Notifications, Multi-Page Forms, Custom Controls.
**Evidence**: https://www.w3.org/WAI/tutorials/forms/ (accessed 2026-07-31; page lists the six sub-pages above and states "This tutorial shows you how to create accessible forms").
**Closest WAI primary sources for file-upload-style forms**: the Forms tutorial's "User Notifications" page (https://www.w3.org/WAI/tutorials/forms/notifications/) — quoted in Section 7.3 — and WCAG 2.2 SC 1.3.1/3.3.1/3.3.2/4.1.3 (Section 2).

### 6.2 MDN `<input type="file">`
- Page: "`<input type="file">`", https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/file (accessed 2026-07-31; "This page was last modified on Apr 17, 2026" — see note: the fetched page footer shows a 2026 modification date).
- Key facts: label association example (`<label for="avatar">…` + `<input type="file">`); `accept` (file type specifiers: extensions, MIME, `audio/*`, `video/*`, `image/*`); `multiple`; `value` = path string, empty if none selected; selected files via `HTMLInputElement.files` (FileList of File objects with name/lastModified/size/type); `cancel` event; `value` cannot be set programmatically; the `accept` attribute is only a hint — "you should make sure that the `accept` attribute is backed up by appropriate server-side validation."
- **Accessibility-relevant note (verbatim)**: "`opacity` is used to hide the file input instead of `visibility: hidden` or `display: none`, because **assistive technology interprets the latter two styles to mean the file input isn't interactive**." (From the "Using file inputs" example discussion.)

### 6.3 MDN drag-and-drop for files — keyboard-accessible pattern
- Page: "File drag and drop", https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API/File_drag_and_drop (accessed 2026-07-31; page last modified Oct 2, 2025). The documented pattern for a drop zone is a **`<label>` wrapping a (hidden) `<input type="file">`**: "we take advantage of a common trick, which is to make the `<input>` invisible, and use its associated `<label>` to interact with the user instead, because `<label>` elements are much easier to style… By virtue of us using the `<label>` and `<input>` elements, no additional JavaScript is needed to implement the file selection UX."
  - Caveat: this example hides the input with `display:none`, which conflicts with MDN's own advice in Section 6.2 (use `opacity:0`). The accessible drop-zone pattern (label + hidden input) is the primary technique; hidden-input method should follow 6.2.
- Page: "Drag operations", https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API/Drag_operations (accessed 2026-07-31; last modified 2025-10-02): events `dragstart/drag/dragend` fire on the dragged item and "can't fire when dragging a file into the browser from the OS"; drop targets cancel `dragover`; `drop` must be cancelled with `preventDefault()` to count as successful; "For the entire course of the drag operation, all device input events (such as mouse or keyboard) are suppressed."
- **Keyboard alternative to drag-and-drop (primary, normative)**: WCAG 2.2 SC **2.5.7 Dragging Movements** (quoted in Section 2) plus its Understanding page https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html (accessed 2026-07-31), which states: "Some people cannot perform dragging movements in a precise manner… An alternative method must be provided…" and gives examples: clicking/tapping the slider track, adjacent up/down buttons for sortable lists, pop-up menu after tapping an item, **"providing a text input can be an acceptable single-pointer alternative to dragging"**, and: "Success Criteria 2.1.1 Keyboard and 2.1.3 Keyboard (No Exception) require dragging features to be keyboard accessible." Sufficient technique **G219**; failure **F108** ("not providing a single pointer method that does not require a dragging movement").

### 6.4 Status messages after upload (aria-live)
- WCAG 2.2 **4.1.3 Status Messages** (quoted in Section 2) requires status messages to be programmatically determinable via role/properties and presented without focus — implemented with `role="status"`/`aria-live="polite"`, `role="alert"`/`aria-live="assertive"`, or `role="progressbar"`/`aria-valuenow`.
- MDN: "ARIA live regions", https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/ARIA_Live_Regions (accessed 2026-07-31): `aria-live="polite"` should be used normally; `aria-live="assertive"` only for time-sensitive/critical notifications; **roles with implicit live-region behavior**: `log`, `status` (add redundant `aria-live="polite"`), `alert` (add redundant `aria-live="assertive"`, but "adding both `aria-live` and `role="alert"` causes double speaking issues in VoiceOver on iOS"), `progressbar` ("A hybrid between a widget and a live region. Use this with `aria-valuemin`, `aria-valuenow` and `aria-valuemax`"), `marquee`, `timer`. `aria-atomic` and `aria-relevant` modifiers documented.

---

## 7. SPA / Focus-Management and Error-Pattern Guidance

### 7.1 Focus management in single-page applications (Deque)
- "Accessible Routing in JavaScript Frameworks", Deque blog, https://www.deque.com/blog/accessible-routing-in-javascript-frameworks/ (published 2020-09-24, accessed 2026-07-31):
  - Without focus management on client-side route changes, "the focus becomes lost or stagnant on the page and the user is not made aware that a new page has appeared… keyboard-only users can also become very frustrated because focus is not managed."
  - Recommendation: "Once a new page is loaded, the focus should go to the most relevant heading of the new page. Preferably this would be the top-level heading… This can be achieved by adding `tabindex="-1"` to the heading and using the component lifecycle… to assign focus."
  - Fallback: "put focus on the body… add `tabindex="-1"` to the body or main container."
  - "With this, also have a live announcement be made to the user that the page has changed, or the new name of the page…"
- "Accessibility Tips in Single-Page Applications", Deque blog (Marcy Sutton), https://www.deque.com/blog/accessibility-tips-in-single-page-applications/ (published 2018-11-07, accessed 2026-07-31): "Make sure that client-side view changes are known to screen reader users by announcing the change in page title, using ARIA live regions and/or focus management." "Get comfortable with focus management in JavaScript, and write it into your automated tests."
- "Manage Focus for Natural Web Page Interaction", Deque University, https://dequeuniversity.com/tips/manage-focus (accessed 2026-07-31): shift focus to new content added in reaction to a user-fired event; move focus to the next logical spot when content is removed; "Make sure focus doesn't move to the top of the web page or becomes lost after a user-fired event"; focus target must have programmatically determinable text.

### 7.2 aria-live regions for async progress
- MDN "ARIA live regions" (Section 6.4) is the primary reference: use `role="status"`/`aria-live="polite"` for non-intrusive progress/status updates (e.g., "Converting file…", "Conversion complete"), `role="alert"` for error outcomes, and `role="progressbar"` with `aria-valuemin/aria-valuenow/aria-valuemax` for determinate progress; do not move focus for status-only announcements (aligns with WCAG 4.1.3).
- WAI APG Alert pattern (Section 3.6): alerts must not take focus and should not auto-dismiss.

### 7.3 Error summary patterns
- **WAI Forms tutorial — User Notifications** (primary), https://www.w3.org/WAI/tutorials/forms/notifications/ (accessed 2026-07-31): for overall feedback, use the main heading, the page `<title>`, a dialog, or an error list at the top of the page. Error list guidance: "The list should have a distinctive heading… Each error listed should: Reference the label of the corresponding form control… Provide a concise description of the error… Provide an indication of how to correct mistakes… Include an in-page link to the corresponding form control." For dynamically inserted error lists (AJAX): "The list of errors should be inserted into a prominent container on the top… this container should have the `role` attribute set to `alert`." "Also, form fields can be associated with the corresponding error message using aria-describedby." Inline: "it is convenient to set the focus to the first `<input>` element that contains an error."
- **GOV.UK Design System "Error summary"** (SECONDARY / supporting example pattern, per task brief), https://design-system.service.gov.uk/components/error-summary/ (accessed 2026-07-31): use at top of page; "move keyboard focus to the error summary (the govuk-frontend javascript will do this for you)"; heading "There is a problem"; link to each answer with an error; same wording as inline messages; add "Error: " to the beginning of the page `<title>`; container uses `<div role="alert">`; inline error messages use `aria-describedby` on the input and visually hidden "Error:" prefix. Marked as a secondary/supporting pattern (national design system, not a standards body).

---

## 8. :focus-visible and the "Focus Visible" Criterion — Current Browser Support

- Page: "`:focus-visible` CSS pseudo-class", MDN, https://developer.mozilla.org/en-US/docs/Web/CSS/:focus-visible (accessed 2026-07-31; "This page was last modified on Apr 17, 2026 by MDN contributors").
- **Baseline status (verbatim)**: "**Baseline: Widely available** — This feature is well established and works across many devices and browser versions. **It's been available across browsers since March 2022.**"
- Semantics: "The `:focus-visible` pseudo-class applies while an element matches the `:focus` pseudo-class and the UA determines via heuristics that the focus should be made evident… (Many browsers show a 'focus ring' by default in this case.)" Browsers no longer show a focus ring for every focused element (e.g., not for pointer clicks on buttons), but do for keyboard navigation and script-managed focus: "focus styles are always required when users are navigating the page with the keyboard or when focus is managed via scripts."
- Practical guidance: use `:focus-visible` to style focus indicators without showing them on pointer clicks; provide a fallback for old browsers: "check supports of `:focus-visible` with `@supports` and repeat the same focus styling in it, but inside a `:focus` rule" — "even if you do not specify anything at all for `:focus`, old browsers will simply display the native outline, which can be enough."
- Accessibility note on the page: "WCAG 2.1 SC 1.4.11 Non-Text Contrast requires that the visual focus indicator be at least 3 to 1."
- **Mapping to WCAG 2.2**: `:focus-visible` is the primary implementation technique for **2.4.7 Focus Visible** (AA, quoted Section 2). WCAG 2.2 additionally adds **2.4.11 Focus Not Obscured (Minimum)** (AA) and **2.4.13 Focus Appearance** (AAA, 2px perimeter + 3:1 contrast) — the AAA criterion's contrast/perimeter math is directly testable with CSS values but not required at AA.
- Secondary corroboration: MDN input/file and ARIA notes do not contradict; Chrome DevTools' Lighthouse manual checks include "Interactive elements indicate their purpose and state" (Section 4.3), which is the human check for focus visibility.

---

## 9. Evidence Index (all sources, URL · title · access date · version/date on page)

Primary (W3C):
1. https://www.w3.org/TR/WCAG22/ · Web Content Accessibility Guidelines (WCAG) 2.2, W3C Recommendation (current revision 12 December 2024; original REC 5 October 2023) · accessed 2026-07-31
2. https://www.w3.org/TR/2023/REC-WCAG22-20231005/ · original WCAG 2.2 REC (5 October 2023) · referenced 2026-07-31
3. https://www.w3.org/TR/2024/REC-WCAG22-20241212/ · current WCAG 2.2 version (12 December 2024) · referenced 2026-07-31
4. https://www.w3.org/WAI/WCAG22/Understanding/ · WCAG 2.2 Understanding index · accessed 2026-07-31 (HTTP 200)
5. https://www.w3.org/WAI/WCAG22/quickref/ · How to Meet WCAG 2.2 (Quickref) · accessed 2026-07-31 (HTTP 200)
6. https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html · Understanding SC 2.5.7 Dragging Movements · accessed 2026-07-31
7. https://www.w3.org/TR/wai-aria-1.2/ · Accessible Rich Internet Applications (WAI-ARIA) 1.2, W3C Recommendation 06 June 2023 · accessed 2026-07-31
8. https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/ · APG Dialog (Modal) Pattern · accessed 2026-07-31 (HTTP 200)
9. https://www.w3.org/WAI/ARIA/apg/patterns/tabs/ · APG Tabs Pattern · accessed 2026-07-31 (HTTP 200)
10. https://www.w3.org/WAI/ARIA/apg/patterns/alert/ · APG Alert Pattern · accessed 2026-07-31
11. https://www.w3.org/WAI/ARIA/apg/patterns/ · APG Patterns index (30 patterns; NO progressbar pattern) · accessed 2026-07-31
12. https://www.w3.org/WAI/test-evaluate/easy-checks/ · Easy Checks – A First Review of Web Accessibility · accessed 2026-07-31; page updated 21 March 2024
13. https://www.w3.org/WAI/test-evaluate/ · Evaluating Web Accessibility Overview · accessed 2026-07-31
14. https://www.w3.org/WAI/tutorials/forms/ · Forms Tutorial (WAI Web Accessibility Tutorials) · accessed 2026-07-31
15. https://www.w3.org/WAI/tutorials/forms/notifications/ · Forms Tutorial: User Notifications · accessed 2026-07-31

Primary (WebAIM):
16. https://webaim.org/projects/screenreadersurvey10/ · Screen Reader User Survey #10 Results (Dec 2023–Jan 2024; 1539 respondents) · accessed 2026-07-31
17. https://webaim.org/techniques/keyboard/ · Keyboard Accessibility (incl. keyboard testing table) · accessed 2026-07-31
18. https://webaim.org/articles/nvda/ · Using NVDA to Evaluate Web Accessibility · accessed 2026-07-31
19. https://webaim.org/articles/jaws/ · Using JAWS to Evaluate Web Accessibility · accessed 2026-07-31
20. https://webaim.org/articles/voiceover/ · Using VoiceOver to Evaluate Web Accessibility · accessed 2026-07-31
21. https://wave.webaim.org/ · WAVE (home) · accessed 2026-07-31
22. https://wave.webaim.org/help · WAVE Help (documented limitations) · accessed 2026-07-31

Primary (MDN / Chrome / Google):
23. https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/file · `<input type="file">` · accessed 2026-07-31 (last modified Apr 17, 2026)
24. https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API/File_drag_and_drop · File drag and drop · accessed 2026-07-31 (last modified Oct 2, 2025)
25. https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API/Drag_operations · Drag operations · accessed 2026-07-31 (last modified Oct 2, 2025)
26. https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API · HTML Drag and Drop API (overview) · accessed 2026-07-31 (last modified Mar 5, 2026)
27. https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/ARIA_Live_Regions · ARIA live regions · accessed 2026-07-31
28. https://developer.mozilla.org/en-US/docs/Web/CSS/:focus-visible · `:focus-visible` pseudo-class (Baseline: widely available, since March 2022) · accessed 2026-07-31 (last modified Apr 17, 2026)
29. https://developer.chrome.com/docs/lighthouse/accessibility/ · Lighthouse accessibility score · accessed 2026-07-31 (last updated 2025-10-22)
30. https://developer.android.com/guide/topics/ui/accessibility/testing · Test your app's accessibility (TalkBack workflow) · accessed 2026-07-31 (page updated 2026-04-16)

Primary (tool vendors / GitHub):
31. https://github.com/dequelabs/axe-core/releases · axe-core releases (latest v4.12.1, 2026-06-09/10) · accessed 2026-07-31
32. https://github.com/dequelabs/axe-core/blob/master/CHANGELOG.md · axe-core CHANGELOG · accessed 2026-07-31
33. https://github.com/dequelabs/axe-core/blob/develop/README.md · axe-core README (57% claim; rule types) · accessed 2026-07-31
34. https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md · axe-core Rule Descriptions (v4.12) · accessed 2026-07-31
35. https://www.deque.com/axe/devtools/ · Axe DevTools (up to 80%; does not replace screen reader testing; Lighthouse-vs-axe note) · accessed 2026-07-31
36. https://squizlabs.github.io/HTML_CodeSniffer/ · HTML_CodeSniffer (WCAG 2.1 + Section 508; client-side JS) · accessed 2026-07-31

Secondary / supporting:
37. https://www.deque.com/blog/accessible-routing-in-javascript-frameworks/ · Deque: Accessible Routing in JavaScript Frameworks (2020-09-24) · accessed 2026-07-31
38. https://www.deque.com/blog/accessibility-tips-in-single-page-applications/ · Deque: Accessibility Tips in Single-Page Applications (Marcy Sutton, 2018-11-07) · accessed 2026-07-31
39. https://dequeuniversity.com/tips/manage-focus · Deque University: Manage Focus for Natural Web Page Interaction · accessed 2026-07-31
40. https://design-system.service.gov.uk/components/error-summary/ · GOV.UK Design System: Error summary (supporting example pattern) · accessed 2026-07-31

---

## 10. Uncertainties, Gaps, and Notes

1. **WCAG 2.2 dates**: The task brief's "5 October 2023" is the original REC date. The live spec is the 12 December 2024 revision. All normative quotes in Section 2 are from the 12 Dec 2024 revision (identical SC text verified against the original REC for the SCs checked; no SC-level wording change was found in the Change Log, but the deliverable should cite the current version).
2. **WAI "Keyboard Testing" page**: https://www.w3.org/WAI/test-evaluate/keyboard/ returned 404 on access date. If the brief requires that exact WAI resource, it appears to have been removed/relocated; Easy Checks and WebAIM keyboard techniques are the verified substitutes. Flag for owner decision.
3. **WAI "Forms — File Uploads" tutorial**: does not exist (verified). The WAI Forms tutorial has no file-upload page; closest primary sources are cited in Section 6.
4. **APG progressbar pattern**: removed from the current APG (404 + absent from index). ARIA 1.2 `progressbar` role + MDN live regions + Lighthouse's `progressbar` name audit are the cited primary references.
5. **axe-core "57%"**: figure is from Deque's own README (marketing-documented); it is the only concrete coverage percentage found in primary tool docs. Deque's axe DevTools page claims "up to 80%" for Deque tools overall (with manual testing still required). Treat both as vendor claims, not independent measurements.
6. **Survey freshness**: WebAIM Survey #10 (Dec 2023–Jan 2024) is the latest published as of access date; no survey #11 was found. Any market-share claim should cite #10 explicitly.
7. **HTML CodeSniffer**: documented standards are WCAG 2.1 (not 2.2); no version number on the project page. Use for quick client-side checks only; do not rely on it for WCAG 2.2 AA evidence.
8. **MDN input/file hiding nuance**: MDN's own File drag and drop example uses `display:none` for the hidden input, while MDN's `<input type="file">` article recommends `opacity:0` because assistive technology treats `display:none`/`visibility:hidden` as non-interactive. For the rebuild, prefer the `opacity:0` technique (or a visually-hidden-but-focusable class).
9. **Quoting fidelity**: All SC quotes in Section 2 were machine-extracted from the spec HTML and spot-checked by hand; list/exception formatting (bullets, "Note" markers) follows the spec structure.
10. **No accounts/auth used**: all evidence was gathered anonymously via public HTTP (curl) and public reader endpoints; no credentials, no browser execution.
