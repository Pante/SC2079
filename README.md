# CZ3004/SC2079 MDP GROUP 14 (AY2023 Semster 2)

This mono-repository contains the entire codebase for MDP. 

It is divided into the following components:
* RPi - Contains the Raspberry Pi codebase that is responsible for communicating between the Android tablet, STM, image recongition service & pathfinding service.
* Image Rec - Contains codes responsible for AI image recognition training. Model used is Yolov8, a You Only Look Once Image recognition algorithm. Detection method is instance segmentation. Includes archive of AI models trained. Dataset for this model can be found [here](https://universe.roboflow.com/my-space-gprvy/yukto-s-c/dataset/61)
* Android - The Android tablet codebase.
* Openapi Simulator Client - An outdated simulator for the pathfinding service. See `Simulator Client` instead. It is built using NextJS and uses a [generated OpenAPI client](https://github.com/OpenAPITools/openapi-generator) to communicate with the pathfinding service. (It might no longer work as it was abandoned after the completion of the MDP checklist).
* Robot - The STM codebase.
* Service - The pathfinding algorithm. It is built using Flask & exposes REST endpoints. These REST endpoints are documented using Swagger/OpenAPI 3.
* Simulator Client - A simulator for the pathfinding service. It is built using NextJS and uses a [generated OpenAPI client](https://github.com/OpenAPITools/openapi-generator) to communicate with the pathfinding service. (It might no longer work as it was abandoned after the completion of the MDP checklist).

Other misc components:
* music - Unused Pokemon theme song that we originally wanted to blast out of a speaker attached to the robot. We unforunately did not have the time to achieve this.

## Members
* [Bohui](https://github.com/bh555)
* [Bryan](https://github.com/BryanTohWS)
* [Junius](https://github.com/Junius00)
* [Matthias](https://github.com/Pante)
* [Melissa](https://github.com/seow2002)
* [Seth](https://github.com/sethlxk)
* [Zhei En](https://github.com/zheien)

## Results

**Task 1:**

![task 1 leaderboard-1](https://github.com/Pante/SC2079/assets/9427324/63c0b7df-2cd6-4ab6-a096-7543b3eee692)


**Task 2:**

![task 2 leaderboard(1)](https://github.com/Pante/SC2079/assets/9427324/2969a2ac-4442-4e5c-a6b2-a2b90acee73e)
