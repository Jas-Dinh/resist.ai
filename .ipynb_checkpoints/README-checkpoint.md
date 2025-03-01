# resist.ai

## Problem Statement 
When patients have bacterial infections, doctors must wait 24-48 for lab results to determine which antibiotics will be effective using classical culture-based testing. During this critical window, they must either use broad-spectrum antibiotics (contributing to resistance) or risk using ineffective antibiotics (endangering the patient). While genetic sequencing can provide information about resistance patterns, current prediction models lack generalized predictive power, user-friendly interfaces, and clear explanations that would make them practical for clinical use. Furthermore, current models do not optimize for using the narrowest effective antibiotic to assist clinicians.

Our solution aims to bridge this gap by combining traditional machine learning with generative AI to create a more interpretable, clinically useful system that helps doctors make faster, more informed antibiotic choices. This proposition represents a critical opportunity as antimicrobial resistance directly causes 1.7 million deaths globally and contributes to 4.95 million deaths annually, while creating $35 billion in productivity losses. The global antimicrobial susceptibility testing market reached $8.70 billion in 2023, with strong growth driven by rising antibiotic resistance and increasing demand for rapid diagnostics.

Key assumptions include healthcare facilities having access to DNA sequencing technology, clinicians' willingness to incorporate AI recommendations into their decision-making process, and our ability to integrate smoothly with existing clinical workflows. We also assume that the speed and cost-effectiveness of genetic sequencing will continue to improve relative to traditional culture methods, making our solution increasingly viable for widespread adoption.

## MVP
Overall the end prototype would be an AI-enhanced clinical decision support system that:
1) Takes bacterial genetic sequence data as input
2) Predicts resistance probabilities for common antibiotics
3) Uses GenAI to:
  - Explain predictions in medical language
  - Suggest optimal treatment strategies
  - Take doctor feedback and convert to signals for re-training
4) Provides web-based interface for easy hospital integration

## Mission Statement
resist.ai aims to help physicians prescribe the most effective antibiotic that is the least likely to contribute to resistance. We strive to create an application able to explain machine generated recommendations and foster trust within human subject matter experts. This way physicians can make faster, more informed, trusted antibiotic choices that slow the global rate of antibiotic resistance development.
