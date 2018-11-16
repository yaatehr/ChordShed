# Chord Shed

_21M.385 Final Project Proposal_

## **Team**

Yaateh Richardson

Kenneth Collins


## Setup

**Install python packages**

> pip install python-rtmidi

> pip install mido

See the python-rtimidi [Docs](https://github.com/SpotlightKid/python-rtmidi/)

See the Mido [Docs](https://mido.readthedocs.io/en/latest/)



## **Project Goal**

Our platform will help beginner and intermediate pianists learn the essentials of accompaniment by teaching users to identify and play chord progressions in major and minor keys.

## **Inspiration / Reference**

**Inspiration**

        A lot of the inspiration behind this for me came from piano lab in 301 class. There are a lot of good resources for learning classical music, but classical music is a lot of muscle memory and doesn&#39;t necessarily teach the essentials of music theory. However simple chord recognition and progressions could really help musicians of all backgrounds.

**Reference**

**Typing.io**

        I use this platform all the time and their paid feature suite actually looks extremely helpful and applicable to our project. They offer monthly plans that help customers to track their performance over time including the following

**Synthesia**
        Piano GUI is very sophisticated and it could be a good basis for our game modes and scoring as well.


_Gameplay:_

[**https://www.youtube.com/watch?v=PFa0Gblm1-w**](https://www.youtube.com/watch?v=PFa0Gblm1-w)

## **Project Description**

**Key Features**

- Helper/Tutor keyboard
  - Skins
- How to accompany things
- Difficulties (call and response)
  - Easy - How to play chord
  - Medium - chord progressions
  - Free play mode - play over
    - ■■Tell people what chords they&#39;re playing
- Customizability
  - Choose a sound (midi bank)
  - Choose a backdrop
    - ■■Correct chords and incorrect visual effects
    - ■■Color theme to match
- Scoring/ constructive feedback
  - Key
  - Progression/Individual chords
  - Track progress over time for a profile
  - Also points for keys hit

**Description**

Our game will function in a similar manner to other gem matching games including synesthesia and guitar hero. The main content will be our custom made subroutines for chord progressions, which can be delivered in various formats to vary the difficulty, including, the information provided along with each Gem (constituent notes, constituent chords, or just a progression given a Key), tempo,  fingering or keyboard indicator help, etc. Thus for each of our difficulty modes, given input will change slightly.

**Hardware -** a piano midi controller, computer

**Software components -**

RTMidi to interpret piano midi signals in python.

Musical syntax to generate progressions and convert to...

Guitar hero Gem recognition software

Random walk/progression building system to keep users on theri toes

Statistic breakdown and data visualization for past results

## **Major Risks / Challenges**

The base functionality of the game should be fairly straightforward given our resources.

For each of our difficulties in our design, the gems will be different. However we will need to come up with some intuitive feedback system that applies across all levels, and conveys all of the possible musical qualities we want.

Another one of our reach goals was teaching people to harmonize, and that could prove difficult to make a concrete system or scoring for appropriate harmonies. This would be the goal if we enabled two handed play.

Finally we were considering adding a free play mode, but making that informative and potentially loading in progressions ( from midis or other musical formats) and mapping them to our gem system may prove difficult.



**Division of Labor**

Dependency Tree

- Midi Input
  - Gem Mapping
    - ■■Content Creation encoding?
      - Custom content or harmonization
    - ■■GUI Representations
      - Easy mode
      - Medium Mode
      - Free Play
      - Customizations
    - ■■Feedback Systems
      - Game Scoring &amp; Progress Metrics
        - Progress over Time
        - Visualizations for Progress
      - Progress
  - Piano Tutor

- Content Creation
  - Encoding could rely on Gem Mapping but not necessarily

Because a lot of the work is parallelizable (see the tree above), we will likely just divide up the timeline goals each week.

## **Timeline / Milestones**

Week - due date

**Week 1- 11/14**

- Get Midi controller inputs
  - Build basic Piano Tutor
- Decide on Gem Mapping Format and start to port guitar hero

**Week 2 - Milestone 1 (11/19)**

- Easy/medium mode content creation
- Complete Gem recognition system

**Week 3 - 11/28 Milestone 2**

- Gameplay visualizations complete
  - GUI Feedback
  - Audible feedback (toggleable?)
- Progress metrics and scoring (not necessarily graphic display) for specific songs

**Week 4 - 12/5**

- Progress over time serialization
- Progress Metric Visualizations
- Skin Customizations (if time)
- Sound/ other customizations
- Free Play (if time)

**Week 5 - 12/10 Gold Master**

- Finishing touches
- Time to complete any delayed milestones
