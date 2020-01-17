# Clock Time vs WorkCenter Time
## Introduction
This document provides an illustrative example of the passage of time on a clock and how it relates to the passage of time in a workcenter.

## Resources
* Resource A can work 1 hour per 1 hour of clock time
* Resource B can work 2 hours per 1 hour of clock time
* Resource C can work 1 hour per 1 hour of clock time

## Jobs
* Job 1000 requires the following *workcenter* hours:
  1. Resource A: 8 hours
  1. Resource C: 4 hours
* Job 2000 requires the following *workcenter* hours:
  1. Resource B: 8 hours
  1. Resource C: 4 hours

## Analysis
Given the above info, the timeline of events will be as follows (all hours shown are clock time):
  1. `t = 0 hours` Simulation starts
  1. `t = 4 hours` Job 2000 completes at Resource B
  1. `t = 8 hours` Job 1000 completes at Resource A
  1. `t = 8 hours` Job 2000 completes at Resource C
  1. `t = 12 hours` Job 1000 completes at Resource C
  1. `t = 12 hours` Simuation complete

Note that Resource C may only begin working on a job when it arrives at the resource, i.e. when the job's prior resources have finished their work.  
Thus, Job 2000 completes at `t = 8 hours` and Job 1000 completes at `t = 12 hours`.

If Resource B were only able to work 1 hour per 1 hour of clock time, the timeline events would be:
  1. `t = 0 hours` Simulation starts
  1. `t = 8 hours` Job 1000 completes at Resource A
  1. `t = 8 hours` Job 2000 completes at Resource B
  1. `t = 12 hours` Job 1000 completes at Resource C
  1. `t = 16 hours` Job 2000 completes at Resource C
  1. `t = 16 hours` Simuation complete

## Takeaway
Ultimately, clock time forecasting is dependent upon workcenter capacity, since it is each workcenters capacity that determines the order in which jobs arrive at subsequent operations.