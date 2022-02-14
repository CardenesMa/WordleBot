# WordleBot 
 
## Author
### Marco Cardenes

---
## Help From
* Kush Bandi
* Niel Wagner-Oke
* Jackson Zemek 
---
## Dependencies
pygame 2.1.0 (SDL 2.0.16, Python 2.9.7)

---
## Notices
It is vitally important that no lines within new_wordle.run() are moved. Gameplay depends on their order.

If you'd like to modify how the game runs, make changes to `wordl.ini` 

Currently, `wordle_ml.py` has no function. It is planned to replace the algorithm in `wordle.py` with a classification model to predict the next word. As it stands, the accuracy of the algorithm in `wordle.py` is about 98.2% when starting with "ADIEU", so the model may be unnecessary.

--- 
## Version History
* 1.0.0 (Current) Initial Release


[Check out the official Wordle here](https://www.nytimes.com/games/wordle/index.html)