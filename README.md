# Covid-19 Representation and Modeling
This is a portion of an larger project that is on hold.  Currently the only public portion is the data and code necessary to generate these animations.  Data is sourced from Johns Hopkins University and the US Census Bureau (county state shape files).  The animations and most recent day images are automatically regenerated everyday at 5:00 am CST.

This may be updated with 'new cases' & 'new deaths'.  Howewver, John's Hopkins data is not monotonicly increasing and fixing their data so as to properly calculate the rolling window was not a priority.

The original goal was to forecast COVID-19 via modelling as a network diffusion process using an STGNN, hence the focus on the USA for which FIPS subunit divisions (counties, parishes, etc.) provide high spatial resolution not found in data for other parts of the world. ![Google Research](https://arxiv.org/pdf/2007.03113.pdf) published their results while I was still doing literature review and busy with my thesis, so I have since moved on.  The code to represent this data as a series of NetworkX graphs may be cleaned up and added in the future.

Scroll down to see just MO/IL.  Images are 1280x720.  Folder link at bottom.

#### USA Most Recent Day
Cummulative Cases          | Cummulative Deaths
:-------------------------:|:-------------------------:
| <img align="left" src=images/jh-log_cum_cases-USA_most_recent_day.png> | <img align="right" src=images/jh-log_cum_deaths-USA_most_recent_day.png> |

#### Animations for all available dates ( USA )
<img src=images/jh-log_cum_cases-USA_anim.gif>
<img src=images/jh-log_cum_deaths-USA_anim.gif>

#### MO / IL Most Recent Day
Cummulative Cases          | Cummulative Deaths
:-------------------------:|:-------------------------:
| <img align="left" src=images/jh-log_cum_cases-MO_IL_most_recent_day.png> | <img align="right" src=images/jh-log_cum_deaths-MO_IL_most_recent_day.png> |

#### Animations for all available dates ( MO/IL )
<img src=images/jh-log_cum_cases-MO_IL_anim.gif>
<img src=images/jh-log_cum_deaths-MO_IL_anim.gif>

![Folder with all animations and most recent day images](https://github.com/jamie-lea-portfolio/Covid-19_Representation_and_Modeling/tree/master/images)
