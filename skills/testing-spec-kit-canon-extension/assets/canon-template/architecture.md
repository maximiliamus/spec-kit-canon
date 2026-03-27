# Architecture

## Canonical Components

The baseline architecture consists of three canonical concerns:

- a Todo collection interface that returns the current Todo list
- a Todo detail interface that returns one Todo by identifier
- a shared Todo projection that keeps the collection and detail views aligned

## Canonical Interactions

The collection and detail interfaces read from the same canonical Todo projection. A collection request returns the available Todo items. A detail request returns the matching Todo when it exists and a not-found outcome when it does not.

## Canonical Constraints

- the baseline canon is read-only
- every interface returns Todo data using the same canonical fields
- later canon drift may extend the available behaviors, but it must preserve the shared Todo projection as the source of truth
