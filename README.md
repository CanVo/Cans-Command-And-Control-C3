
# Basic Command And Control (C2)
The repository includes a fundamental and simple Command and Control (C2) setup. My motivations and intentions for this were to gain an understanding of the workings of a C2 flow, learn the process of creating a suitable environment for it, and share this knowledge with friends and family.

In its current state, to successfully create a connection between server and target, the following assumptions are in-place:
* Assumed server and target machine can talk to each other through the network (either internally or externally).
* Assumed target machine has Python installed
* Assumed Target has agent script dropped and residing on it (possibly through exploitation of a vulnerability or malicious file downloaded).
* Assumed agent is executing at admin privileges (possibly through exploitation such as privilege escalation).


# Requirements
- Python 3.10
- Flask 2.3.3
- Server to host the C2 Server
- Server to run agent / implant payload


# Disclaimers / Notes
* As the creator of this project and its associated source code, want to make it clear that the project was created exclusively for research and educational purposes. The primary goal is to provide insights into the construction and workflow of Command and Control software (C2's) for educational use.

* I explicitly state that I do not condone or encourage any unethical or malicious activities related to the use, modification, or distribution of this software or similar technologies. The project is intended to be used responsibly and in compliance with legal and ethical standards.

* I accept no liability for any consequences arising from the use, misuse, or any other activities associated with this software. The project is provided "as-is" without any warranty, and I disclaim any responsibility for its application in real-world scenarios.

* Users are encouraged to use this project responsibly and in accordance with applicable laws and regulations. Any actions taken with this software are the sole responsibility of the user.

* By using, modifying, or distributing this software, you acknowledge and agree to the terms of this disclaimer.

* I won't be actively involved in working on or updating this project at the moment due to my current commitments to other projects. While there's a possibility that I might reconsider in the future, it is highly unlikely.