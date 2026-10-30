# Reliable UDP Using ARQ Protocols

## Computer Networks Laboratory Project Documentation

**Institution:** KIIT  
**Department:** Computer Science and Engineering  
**Course/Section:** CSE 23  
**Faculty:** Vishal Meena  
**Repository:** https://github.com/rakshitswarnadeep/ReliableUDP-ARQ  
**Date:** 30 October 2026

## Current team

Member                     Roll number

\---

Swarnadeep Rakshit            24051297
Surisetty Sai Akhilesh        24051746
Swastik Dhople                24051670

\---

## 1\. Abstract

UDP is a connectionless transport-layer protocol. It provides
low-overhead communication, but does not itself guarantee delivery,
ordering, or retransmission. This project demonstrates reliable file
transfer over UDP using three Automatic Repeat reQuest (ARQ) strategies:
Stop-and-Wait, Go-Back-N, and Selective Repeat.

The system uses UDP sockets, shared packet helpers, and a channel
emulator to simulate network impairments such as packet loss and
corruption. File integrity is checked using SHA-256 hashes. Selective
Repeat is evaluated at different simulated packet-loss rates using
transfer time and goodput.

## 2\. Problem statement

A UDP datagram may be lost or corrupted during transmission. UDP does
not provide built-in retransmission or delivery guarantees. Applications
that need reliable transfer must implement their own recovery mechanism.

This project implements ARQ protocols above UDP. The sender transmits
data packets, the receiver returns acknowledgements (ACKs), and the
sender uses acknowledgements and timeouts to decide whether
retransmission is required.

## 3\. Objectives

* Implement reliable file transfer over UDP.
* Study Stop-and-Wait, Go-Back-N, and Selective Repeat ARQ.
* Simulate network impairment through a channel emulator.
* Observe acknowledgement and retransmission behaviour.
* Verify received-file integrity using SHA-256.
* Measure Selective Repeat transfer time and goodput at different
simulated loss rates.
* Compare the behaviour and trade-offs of the three ARQ strategies.

## 4\. Technologies and tools

Technology/tool    Purpose

\---

Python             Protocol implementation and experiment scripts
UDP sockets        Sender--receiver communication
Git and GitHub     Version control and team collaboration
Channel emulator   Simulation of network impairment
PowerShell         Running scripts and checking hashes on Windows
CSV and Excel      Storing and reviewing experiment results

## 5\. Background: UDP and ARQ

### 5.1 UDP

User Datagram Protocol (UDP) is a connectionless transport-layer
protocol. It sends datagrams without establishing a connection first.
UDP has relatively low overhead, but it does not guarantee delivery,
ordering, or retransmission.

### 5.2 Automatic Repeat reQuest (ARQ)

ARQ is a reliability technique in which a sender uses acknowledgements
and retransmissions to recover from packet loss or transmission errors.
A sender may retransmit a packet when its acknowledgement is not
received within the expected time.

## 6\. ARQ protocols implemented

### 6.1 Stop-and-Wait ARQ

1. The sender transmits one data packet.
2. The sender waits for an acknowledgement.
3. After receiving the expected ACK, it sends the next packet.
4. If the ACK is not received before the timeout, the sender
retransmits the packet.

**Advantage:** Simple to understand and implement.  
**Limitation:** The sender waits after every packet, which can reduce
link utilisation.

### 6.2 Go-Back-N ARQ

1. The sender can transmit several packets without waiting for an ACK
after every individual packet, subject to its sliding-window limit.
2. The receiver acknowledges packets according to the protocol's
sequence rules.
3. If a packet is missing, the sender goes back to the missing packet
and retransmits it and subsequent outstanding packets as required.

**Advantage:** Pipelining allows multiple packets to be in transit.  
**Limitation:** A loss can cause retransmission of later outstanding
packets that may already have reached the receiver.

### 6.3 Selective Repeat ARQ

1. The sender can have multiple packets outstanding within its sending
window.
2. Packets are acknowledged individually.
3. The receiver can buffer valid out-of-order packets.
4. The sender retransmits only packets that still require recovery.

**Advantage:** Avoids some unnecessary retransmissions.  
**Limitation:** Requires more state management and receiver buffering.

### 6.4 Comparison

\---

Feature           Stop-and-Wait     Go-Back-N                 Selective Repeat

\---

Sending behaviour One packet at a   Multiple packets in a     Multiple packets
time              window                    in a window

ACK handling      Waits for each    Cumulative/window-based   Individual packet
packet's ACK      behaviour                 ACK

Recovery          Retransmit        Retransmit missing packet Retransmit
unacknowledged    and subsequent            packets needing
packet            outstanding packets as    recovery
required

Receiver          Minimal           Usually discards          Buffers
buffering                           out-of-order packets      out-of-order
packets

Main trade-off    Simple, lower     Pipelining, possible      Efficient
utilisation       extra retransmissions     recovery, more
complexity
---

## 7\. System design and packet format

The project uses UDP sockets for communication and shared packet helpers
in `common.py`. The packet format uses:

* Magic value: `RDT1`
* Packet-type field
* Sequence/acknowledgement-related fields
* Checksum

The implementation defines three packet types:

Packet type   Purpose

\---

`DATA`        Carries file data
`ACK`         Acknowledges received data or protocol progress
`END`         Indicates the end of the file transfer

The shared packet helpers keep packet creation and parsing consistent
across protocol implementations. The checksum supports detection of
corrupted packets. The channel emulator introduces simulated network
impairment.

**Implementation note:** Exact field offsets, integer widths, checksum
coverage, timeout values, and protocol-specific state transitions must
be confirmed from the final source code before the presentation. Do not
assume a field's meaning without checking its implementation.

## 8\. Repository structure

Repository: https://github.com/rakshitswarnadeep/ReliableUDP-ARQ

\---

File/folder                         Role

\---

`common.py`                         Shared packet definitions and
packet helper functions

`channel\_emulator.py`               Simulates channel impairment

`protocols/`                        Sender and receiver implementations

`tests/`                            Tests for shared functionality and
channel-emulator behaviour

`analysis/`                         Experiment analysis material

`graphs/`                           Performance graphs

`docs/`                             Project documentation

`reports/`                          Final project report

`config.json`                       Project configuration

`run\_sender.py`, `run\_receiver.py`  Top-level run scripts, where
applicable

`run\_experiments.py`                Experiment runner

`requirements.txt`                  Python dependency list

`README.md`                         Repository overview and usage
instructions
---

Check the current scripts and `config.json` for exact command-line
arguments and configuration keys.

## \## 9. Team contributions

## 

## | Member | Roll number | Responsibilities |

## |---|---|---|

## | Swarnadeep Rakshit | 24051297 | Selective Repeat ARQ, channel emulator, experiments and performance graphs. |

## | Surisetty Sai Akhilesh | 24051746 | Go-Back-N ARQ, packet-loss testing, result verification and debugging. |

## | Swastik Dhople | 24051670 | Stop-and-Wait ARQ, common packet implementation and UDP communication. |

##| Sunetra Das | 2405391 | Channel emulator, network-condition testing, packet loss, corruption, duplication,                         reordering, delay and jitter testing, file-integrity verification, performance analysis and graphs. |

## 10. Testing and validation

The project was tested by running sender and receiver programs in
separate terminals and transferring files. The project history includes
successful file-transfer checks for Stop-and-Wait, Go-Back-N, and a
small-file Selective Repeat test. A larger Selective Repeat test was
also used for performance measurements.

A successful transfer should be checked by: 1. Confirming that the
receiver creates the expected output file. 2. Confirming that sender and
receiver report completion. 3. Comparing original and received file
sizes. 4. Comparing SHA-256 hashes.

### 10.1 SHA-256 check

On Windows PowerShell, run these commands from the project directory,
adjusting paths if necessary:

``` powershell
Get-FileHash .\\protocols\\large\_test.bin -Algorithm SHA256
Get-FileHash .\\received\_test.txt -Algorithm SHA256
```

If the SHA-256 values are identical, that is strong evidence that the
original and received files contain identical data.

## 11\. Selective Repeat performance experiment

### 11.1 Setup

Parameter                                  Value

\---

Test file size           1 MiB (1,048,576 bytes)
Window size                                    4
Random seed                                    1
Simulated loss rates           0%, 10%, 20%, 30%

Sender and receiver were run in separate terminals. The received file
was checked using SHA-256.

### 11.2 Metrics

**Transfer time** is the elapsed time required to complete the file
transfer.

**Goodput** is the amount of useful file data delivered per second.

\[ `\\text{Goodput}`{=tex} =
`\\frac{\\text{File size in bytes}}{\\text{Transfer time in seconds}}`{=tex}
]

### 11.3 Recorded results

\---

&#x20;     Simulated loss rate Transfer time (seconds)  Goodput (bytes/second)

\---

&#x20;                      0%                  78.206               13,407.87

                      10%                 118.179                8,872.78

                      20%                 180.000                5,825.42

                      30%                 243.531                4,305.72

\---

These are recorded observations from the project's working analysis, not
guaranteed timings. Transfer time can vary between runs because of
random loss, retransmissions, timeouts, and system scheduling.

### 11.4 Interpretation

The recorded results show that transfer time increased and goodput
decreased as simulated packet loss increased. A higher loss rate can
cause more recovery work, including retransmissions and waiting for
acknowledgements or timeouts.

The measurements illustrate the effect of simulated loss. They are not
universal performance guarantees. Repeated trials and averages would
make the comparison more robust.

## 12\. AI tools and assistance disclosure

This section must be edited to reflect the team's actual use of AI
tools, prompts, code changes, and verification. Do not claim that all
code was independently written if AI-generated code was used.

### 12.1 Areas of assistance to confirm

AI assistance may have been used for activities such as:

* Explaining UDP, ARQ concepts, sliding windows, acknowledgements,
timeouts, and retransmissions.
* Helping interpret Python errors and debug code.
* Suggesting test cases and explaining terminal output.
* Helping organise experiment results and explain goodput.
* Improving documentation and preparing viva explanations.

**Retain only the activities that actually occurred.** If AI generated
or substantially modified a code section, identify the relevant file and
describe that assistance specifically.

### 12.2 Human verification

AI suggestions are not proof that an implementation works. The team
should verify code by running the programs, inspecting sender and
receiver output, testing file transfers, reviewing experiment results,
and comparing file hashes. The team remains responsible for
understanding, testing, and explaining the submitted implementation.

### 12.3 Suggested disclosure statement

> We used AI tools as an assistance resource for understanding concepts,
> troubleshooting selected implementation issues, organising
> documentation, and preparing explanations, where applicable. AI
> suggestions were reviewed by the team and checked against the project
> code and test outputs. The team is responsible for the final
> implementation, experiment results, and submitted documentation.

Edit this statement if actual AI use was narrower or broader. Be
prepared to identify which files or sections received AI assistance and
what changes the team made after reviewing suggestions.

## 13\. Challenges and learning outcomes

The project provides practical experience with:

* Building reliable behaviour on top of an unreliable transport
protocol.
* Implementing sequence numbers, acknowledgements, checksums, and
retransmission logic.
* Understanding the differences between the three ARQ methods.
* Testing sender and receiver programs as separate processes.
* Simulating packet loss and observing recovery.
* Checking file integrity with cryptographic hashes.
* Measuring transfer time and calculating goodput.
* Collaborating through Git and GitHub.

Add specific debugging challenges and the actual fixes encountered by
the team before the final presentation.

## 14\. Limitations

* A simulated channel does not represent every characteristic of a
real network.
* Transfer times vary between runs.
* The recorded performance experiment focuses on Selective Repeat at
four loss rates.
* More repeated trials would provide stronger average-performance
evidence.
* Comparing all three protocols under identical conditions would
provide a broader evaluation.
* Protocol-specific details must be interpreted from the final
submitted code.

## 15\. Future enhancements

* Repeat each loss-rate experiment several times and report averages
and variability.
* Record retransmission counts, timeout events, and packet-delivery
statistics.
* Extend the emulator to test additional network conditions, where
supported.
* Compare all three ARQ protocols under identical file sizes and
channel conditions.
* Improve automated testing and document exact run commands and
configuration options.

