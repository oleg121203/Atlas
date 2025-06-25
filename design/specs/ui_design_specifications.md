# UI Design Specifications for Atlas (ASC-024)

This document provides detailed design specifications for the UI redesign of the Atlas application as part of ASC-024. These specs are intended for developers to implement the updated user interface, focusing on usability, accessibility, user feedback mechanisms, and customizable themes/layouts as outlined in the UI Enhancement Strategy, wireframes, mockups, and feedback iterations.

## Table of Contents
- [Overview](#overview)
- [Design System](#design-system)
- [Navigation Specifications](#navigation-specifications)
- [Workspace Specifications](#workspace-specifications)
- [Task Creation Flow Specifications](#task-creation-flow-specifications)
- [Context-Aware Panels Specifications](#context-aware-panels-specifications)
- [Accessibility Specifications](#accessibility-specifications)
- [User Feedback Mechanism Specifications](#user-feedback-mechanism-specifications)
- [Customizable Themes and Layouts Specifications](#customizable-themes-and-layouts-specifications)
- [Interaction Behaviors](#interaction-behaviors)
- [Assets](#assets)
- [Implementation Notes](#implementation-notes)

## Overview

These specifications translate the high-fidelity mockups and feedback iterations into actionable guidelines for PySide6 development. All measurements are in pixels (px) unless otherwise noted, and colors are provided in hexadecimal format. The goal is to ensure a consistent, accessible, and user-friendly interface for Atlas.

## Design System

### Color Palette
- **Primary Blue**: #3B82F6 (used for primary buttons, active states)
- **Secondary Blue**: #1E3A8A (used for header gradient start)
- **Accent Yellow**: #F59E0B (used for highlights, active tab underlines)
- **Success Green**: #38A169 (used for success messages, AI suggestions)
- **Error Red**: #E53E3E (used for error states, validation feedback)
- **Neutral Light Gray**: #F7FAFC (light theme background)
- **Neutral Dark Gray**: #1A202C (dark theme background)
- **Card Light**: #FFFFFF (light theme cards)
- **Card Dark**: #2D3748 (dark theme cards)
- **Text Dark**: #4A5568 (primary text in light theme)
- **Text Light**: #CBD5E1 (primary text in dark theme)
- **Sidebar Dark**: #1E293B (sidebar background in all themes)
- **High-Contrast Background**: #000000
- **High-Contrast Text**: #FFFFFF
- **High-Contrast Accent**: #FFFF00

### Typography
- **Font Family**: Roboto (fallback to system sans-serif)
- **Heading Size**: 20px, bold (used for section titles, modal headers)
- **Body Text Size**: 16px, regular (used for general content, buttons)
- **Subtext Size**: 14px, regular (used for secondary labels, tooltips)
- **Breadcrumb Size**: 12px, regular (used for breadcrumb navigation)
- **Line Height**: 1.5 for body, 1.2 for headings
- **Accessibility Adjustment**: Allow text size scaling from 12px to 24px for body text, maintaining proportionality.

### Icons
- **Library**: Material Design Icons
- **Default Size**: 24px (used for toolbar, navigation)
- **Button Icon Size**: 20px (used within buttons)
- **Color**: Matches text color of context (e.g., #4A5568 in light theme, #CBD5E1 in dark)
- **Hover State**: Lighten by 20% or switch to accent color (#F59E0B) for active icons.

### Spacing and Layout
- **Padding Standard**: 16px (used for card interiors, modal content)
- **Padding Compact**: 8px (used for tight layouts, button padding)
- **Margin Standard**: 16px (used between major components)
- **Margin Compact**: 8px (used between related elements like form fields)
- **Border Radius**: 4px for cards and buttons, 8px for larger containers like modals and sidebar.
- **Shadow**: 0 2px 4px rgba(0,0,0,0.1) for light theme cards, 0 2px 4px rgba(255,255,255,0.1) for dark theme.

## Navigation Specifications

### Header Bar
- **Height**: 60px
- **Background**: Gradient from #1E3A8A (left) to #3B82F6 (right)
- **Logo**: Left-aligned, 40px height, 16px left margin
- **Navigation Tabs**:
  - Text: 16px Roboto, white (#FFFFFF)
  - Spacing: 24px between tabs
  - Active State: Underline with 2px solid #F59E0B
  - Hover State: Text lightens to 90% opacity, cursor pointer
- **Search Bar**:
  - Position: Right-aligned, 16px right margin
  - Size: 200px width, 32px height
  - Style: White 1px border, 4px radius, background semi-transparent white (rgba(255,255,255,0.2))
  - Placeholder: 'Search Atlas...', 14px italic, rgba(255,255,255,0.7)

### Sidebar (Collapsible)
- **Width**: 250px (expanded), 60px (collapsed)
- **Background**: #1E293B
- **Toggle Icon**: White chevron, 24px, top-right of sidebar, rotates 180° on collapse
- **Sub-Navigation Items**:
  - Text: 16px Roboto, #CBD5E1 (normal), white (#FFFFFF) on hover
  - Active Item: Left 4px stripe in #F59E0B
  - Padding: 12px left, 8px top/bottom
  - Hover: Background rgba(255,255,255,0.1)
- **Border**: Right 1px solid rgba(255,255,255,0.1)

### Breadcrumb Trail
- **Position**: Below header, 16px left margin, 8px top margin
- **Text**: 12px Roboto, #718096 (light theme), #A0AEC0 (dark theme)
- **Separator**: '>' with 8px padding on either side
- **Clickable Segments**: Underline on hover, cursor pointer, color #3B82F6

## Workspace Specifications

### Main Content Area
- **Width**: 80% of viewport width (desktop), 100% (mobile < 768px)
- **Background**: #F7FAFC (light), #1A202C (dark)
- **Padding**: 16px on all sides
- **Layout**: Responsive grid, minimum card width 300px, 16px gutter
- **Cards**:
  - Background: #FFFFFF (light), #2D3748 (dark)
  - Border Radius: 4px
  - Shadow: As per design system
  - Padding: 16px
  - Title Text: 18px Roboto bold, body text 16px regular

### Contextual Toolbar
- **Position**: Sticky, top of content area (below breadcrumb if present)
- **Height**: 48px
- **Background**: Matches content background, bottom border 1px #E2E8F0 (light) or #4A5568 (dark)
- **Buttons**:
  - Primary: Background #3B82F6, text white, hover lightens 10%
  - Secondary: Background #A0AEC0, text white, hover lightens 10%
  - Size: 32px height, 100px min-width, 4px radius
  - Icon: 20px, left-aligned with 8px right padding before text (14px Roboto)

## Task Creation Flow Specifications

### Modal Window
- **Size**: 600px width, auto height (max 80% viewport height)
- **Position**: Centered, with backdrop overlay rgba(0,0,0,0.5)
- **Background**: #FFFFFF (light), #2D3748 (dark)
- **Border**: 1px #E2E8F0 (light), #4A5568 (dark), 8px radius
- **Padding**: 24px header, 16px body and footer
- **Header**:
  - Title: 20px Roboto bold, color matches primary text
  - Close Button: 24px Material 'close' icon, top-right, hover #E53E3E
- **Fields**:
  - Input: 40px height, 1px border #A0AEC0 (light) or #4A5568 (dark), 4px radius
  - Focus State: 2px outline #3B82F6
  - Label: 14px Roboto, 8px above field, color matches primary text
  - AI Suggestion: 12px italic, #38A169, below field, fade-in animation
- **Advanced Options Button**:
  - Style: Outline 1px #F59E0B, text #F59E0B, 32px height, 4px radius
  - Text: 'Show Advanced Options', 14px Roboto
  - Icon: Chevron down, rotates 180° on expand
  - Hover: Background rgba(245,158,11,0.1)
  - Tooltip: On first use, small tooltip 'More settings available'
- **Footer Buttons**:
  - 'Save': Background #3B82F6, text white
  - 'Save & New': Outline 1px #3B82F6, text #3B82F6
  - 'Cancel': Background #A0AEC0, text white (light theme) or outline in dark
  - Size: 32px height, 4px radius, 16px spacing

## Context-Aware Panels Specifications

### Dynamic Side Panel
- **Width**: 300px (default), resizable via left drag handle (5px wide, cursor resize)
- **Position**: Right side, full height of content area
- **Background**: #EDF2F7 (light), #1E293B (dark)
- **Border**: Left 1px #E2E8F0 (light), #4A5568 (dark)
- **Shadow**: Left subtle shadow for depth (0 -2px 4px rgba(0,0,0,0.1))
- **Sections**:
  - Header: 16px Roboto bold, chevron toggle (rotates on collapse), 16px padding
  - Content: 12px padding, 16px text
  - Action Buttons: #3B82F6 text, underline on hover, 14px Roboto
- **Drag-and-Drop**:
  - Dragged Item: Opacity 0.6, clone follows cursor
  - Drop Zone: Dashed 2px #3B82F6 border, semi-transparent blue overlay (rgba(59,130,246,0.2)) on hover
  - Confirmation Tooltip: 'Task moved to [location]', #38A169, fades after 2s

## Accessibility Specifications

### High-Contrast Mode
- **Background**: #000000
- **Text**: #FFFFFF
- **Buttons/Accents**: #FFFF00
- **Borders**: 1px #FFFFFF
- **Focus Indicator**: 3px solid #FFFF00 with 1px glow effect (rgba(255,255,0,0.3))
- **Toggle**: Available in Settings > Accessibility and quick toolbar

### Text Size Adjustment
- **Range**: 12px to 24px for body text, proportional scaling for headings (1.25x body)
- **Control**: Slider in Settings > Accessibility, live preview text updates
- **Layout**: Ensure no overlap or clipping at 200% zoom (24px body text)

### Keyboard Navigation
- **Focus Order**: Logical tab order (header -> sidebar -> content -> panels)
- **Focus Indicator**: 2px solid #3B82F6 (normal themes), 3px #FFFF00 (high-contrast), animated subtle pulse (1s ease-in-out)
- **Shortcuts**: Display overlay with '?' key, listing shortcuts (e.g., Ctrl+T for new task)

### Screen Reader Support (ARIA)
- **Labels**: Add `aria-label` to all interactive elements without visible text (e.g., icon-only buttons)
- **Roles**: Define `role` for custom widgets (e.g., `role="navigation"` for sidebar)
- **Live Regions**: Use `aria-live="polite"` for dynamic updates (e.g., task moved notifications)
- **Focus Management**: Programmatically set focus on modal open, return focus on close

## User Feedback Mechanism Specifications

### In-App Feedback Form
- **Access**: Button in header (chat bubble icon, 24px) or Settings > Feedback
- **Modal**:
  - Size: 500px width, auto height
  - Fields: Rating (1-5 stars, yellow #F59E0B), Category dropdown (Bug, Feature, UI, Other), Comment textarea (100px height)
  - Buttons: 'Submit' (#3B82F6), 'Cancel' (#A0AEC0)
- **Submission**:
  - Backend: POST to internal endpoint (to be defined), anonymized data
  - Confirmation: Toast notification 'Feedback received, thank you!' in #38A169

### Feedback Analytics (Developer Note)
- **Track**: Clicks, navigation paths, feature usage frequency (anonymized)
- **Storage**: Local SQLite or cloud if sync enabled, with opt-out in Settings
- **Visualization**: Internal admin view (future task), aggregate data only

## Customizable Themes and Layouts Specifications

### Themes
- **Options**: Light (default), Dark, System (follows OS setting), High-Contrast
- **Custom Theme**:
  - Color Picker: For primary, secondary, accent colors
  - Preview: Live update small UI snippet in Settings > Appearance
  - Save: Store in user profile, sync if cloud enabled
- **Switching**: Instant toggle in Settings > Appearance or quick toolbar icon
- **Persistence**: Retain across sessions, sync across devices if logged in

### Layouts
- **Draggable Panels**:
  - Supported Areas: Sidebar (left), Context Panel (right), optional bottom tray
  - Handle: 5px draggable edge, cursor resize
  - Constraints: Min width 200px, max 50% viewport
  - Snap Back: Return to default if dragged off-screen
- **Presets**:
  - Options: Default, Developer (wide code panel), Designer (focus on visual tools)
  - Save Custom: 'Save Current Layout As...' in Settings > Layout
  - Load: Apply instantly with 0.3s transition animation
- **Persistence**: Store in user profile, sync if cloud enabled

## Interaction Behaviors

### Animations
- **Modal Open/Close**: Scale from 0.9 to 1.0 (open), 1.0 to 0.9 (close), 0.3s ease-out
- **Panel Slide**: Sidebar and context panel slide in/out, 0.3s ease-in-out
- **Fade**: AI suggestions, tooltips fade in 0.5s, fade out 0.3s
- **Theme Switch**: Cross-fade backgrounds and text, 0.3s linear
- **Error Feedback**: Shake animation on invalid input (0.2s, 3px left-right)

### Hover States
- **Buttons**: Lighten background by 10% (or darken outline), cursor pointer
- **Links/Actions**: Underline text, cursor pointer, color to #3B82F6 if not already colored
- **Icons**: Lighten by 20% or switch to accent #F59E0B if contextual
- **Tooltips**: Appear after 0.5s delay, small box with 12px text, background #2D3748 (dark) or #FFFFFF (light), shadow

### Transitions
- **Tab Switch**: Fade content 0.2s, no flicker (maintain old content until new is ready)
- **Collapsible Sections**: Height transition 0.3s ease-in-out
- **Drag-and-Drop**: Smooth follow with cursor, snap back 0.2s if invalid drop

## Assets

**Note**: In a real project, assets would be exported from Figma as PNG/SVG. Here, they are described for simulation.
- **Icons**: Use Material Design Icon set, available via PySide6 resource or external library. Key icons include: home, tasks, chat, plugins, settings, search, close, chevron (up/down/left/right), add, edit, delete.
- **Logo**: Atlas logo, 40px height PNG/SVG, white variant for header.
- **Placeholder Images**: For task cards or user profiles, use 1:1 gray placeholder (#A0AEC0).
- **Export Location**: Store in `resources/ui/assets/` folder for PySide6 QRC integration (to be created during implementation).

## Implementation Notes

- **Framework**: Use PySide6 for UI implementation, leveraging QWidget, QLayout for responsive grids.
- **Styling**: Use QSS (Qt Style Sheets) mirroring CSS properties from this spec (e.g., background-color, border-radius).
- **Accessibility**: Implement ARIA equivalents via Qt's accessibility API (QAccessible), ensure keyboard navigation with focus policies.
- **Themes**: Implement theme switching via QSS reload or palette changes, store user prefs in QSettings or custom profile.
- **Performance**: Optimize animations with QPropertyAnimation, avoid heavy repaints during theme/layout changes.
- **Testing**: Test UI at multiple resolutions (minimum 1280x720), validate accessibility with macOS VoiceOver.
- **Priority**: Start with navigation and accessibility updates, as they impact the entire app experience.
- **Documentation**: Update internal UI component docs with new styles and behaviors post-implementation.

---

These design specifications provide a comprehensive guide for implementing the UI redesign for Atlas under ASC-024. If there are any adjustments or additional details needed before coding begins, please let me know. Otherwise, I will proceed with the implementation phase.
