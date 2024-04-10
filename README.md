# Gomoku MCTS agent Tobias Bosch

## Geprobeerde Should/Could-haves

### Rollout Strategie

Ten eerste voer ik meerdere rollouts uit per expansion.
Ik heb het aantal rollouts vastgesteld op 200 door te timen of de bot binnen de tijdslimiet blijft (+/- 20 ms),
terwijl het beter performt in de tests. Ik heb verschillende hoeveelheden geprobeerd, waaruit bleek dat 200 rollouts
maximaal 20 ms te lang duurde, terwijl het 12 tot 13 v/d 13 tests behaalde. 150 haalde meestal 11 tot 12, en 250 zorgde vaak voor een 
tijdsoverschrijding van 30 ms, wat ik teveel vond.

Ik heb ook een alternatieve rollout strategie geprobeerd.
In plaats van volledig willekeurig, prioritiseert het moves die gemaakt kunnen worden
rondom de laatst gemaakte move.
De gedachte is dat een speler moet winnen door veel moves te maken dichtbij hun anderen om 5 op een rij te krijgen,
dus zal een gemiddelde speler veel moves maken rondom hun vorige moves.

Ik heb deze rollout naar mijn weten succesvol geimplementeerd, en deze een paar tientallen keren de tests laten doen,
en deze laten spelen tegen de standaard rollout. Naar mijn verbazing, deed de standaard rollout het in de tests beter.
In het spelen tegen elkaar gingen de bots ongeveer gelijk op, zonder duidelijke verbetering.

Hierdoor heb ik uiteindelijk gekozen voor 200 rollouts per expansion, met de standaard volledig random rollout strategie.