# MVI Pattern Implementation Guide

## Overview

This application implements the **Model-View-Intent (MVI)** architecture pattern for state management in React. MVI is a unidirectional data flow pattern that provides predictable state transitions, excellent testability, and powerful debugging capabilities.

## Core Concepts

### Intent (User Actions)
**Intents** represent user actions or system events that express an intention to change state.

### Model (State Tree)
The **Model** is a single, immutable state tree that represents the entire UI state for a feature.

### View (UI Components)
**Views** are pure functions of the model that render the UI.

## Data Flow

1. User interacts with the View
2. View dispatches an Intent
3. Middleware intercepts for side effects
4. Reducer produces new state
5. Selectors derive data
6. View re-renders

See full documentation at: /frontend/docs/MVI_PATTERN.md
