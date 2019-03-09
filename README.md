# GNUCash Gource Viz

[Gource](https://gource.io/) is a tool for visualizing code history, but
why shouldn't we leverage it to visualize ANY history that can be visualized
in a tree structure?

This project is aimed at abusing Gource to visualize *account history over
time* as generated by [GNUCash](https://www.gnucash.org/), a free accounting
software package. To generate an appropriate transaction dump, go to
File > Export > Export Transactions to CSV. Enable "use quotes" and "simple
layout", then select all your accounts on the next page, and save a dump
file.

## Usage

This script parses through GNUCash transaction dumps and generates
Gource-compatible logs.

**[WIP; not done yet]**

