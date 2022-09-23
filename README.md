# UltimateDrumScorerPro

## Controls
| Key    | Specification       | Result                      |
|--------|---------------------|-----------------------------|
| Scroll |                     | Zoom                        |
| Drag   | On Background       | Moves the page              |
| Drag   | On piece of content | Moves that piece of content |

## Note drawing
Eventually there will be multiple methods that you can choose from! At the moment only the official note drawing rules
are being created.

## Storage
Notes are stored a tree, which is usually a binary tree, excluding the first layer which is beats in the bar, and also
triplets (or other etc.)
```
1  kick
9     snare
13     kick
17         kick
19         snare
        # Line goes to here
23         kick
25         snare
27         snare
29         snare
33             snare,kick
34             kick
35             snare
36             snare
        # Line goes to here
37             snare,kick
38             kick
```
Which would look like [this](https://www.mikeslessons.com/groove/?TimeSig=5/4&Div=32&Tempo=80&Measures=1&H=|----------------------------------------|&S=|--------O---------O-----O-O-O---O-OO--O-|&K=|o-----------o---o-----o---------oo----oo|)