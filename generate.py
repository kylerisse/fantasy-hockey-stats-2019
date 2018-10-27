#!/usr/bin/env python3

import csv
import datetime
import jinja2
import os

scheduleFile = "schedule.csv"
mailTemplate = "template.j2"
numTeams = 10
maxTeamName = 15
numWeeks = 20
pointsPerWeek = 12


def readSchedule(file):
    try:
        fh = open(file)
    except:
        print("cannot open " + file)
        exit(1)
    schrdr = csv.reader(filter(lambda row: row[0] != '#', fh))
    sch = []
    for row in schrdr:
        if len(row) not in [3, 5]:
            print("bad row in " + file + " " + str(row))
            exit(1)
        sch.append(row)
    fh.close()
    return sch


def extractTeams(schedule):
    tms = []
    for row in schedule:
        if row[1] not in tms:
            tms.append(row[1])
        if row[2] not in tms:
            tms.append(row[2])
    if len(tms) != numTeams:
        print(sorted(tms))
        print(str(len(tms)) + " not equal " + str(numTeams))
        exit(1)
    for t in tms:
        if len(t) > maxTeamName:
            print(t + " exceeds max length " + str(maxTeamName))
            exit(1)
    return tms


def generateMatches(schedule):
    mtchs = []
    for row in schedule:
        d = row[0]
        t1 = row[1]
        t2 = row[2]
        if len(row) < 5:
            for m in genFutureMatches(d, t1, t2):
                mtchs.append(m)
        else:
            t1w = int(row[3])
            t2w = int(row[4])
            for m in genPastMatches(d, t1, t2, t1w, t2w):
                mtchs.append(m)
    return mtchs


def genPastMatches(date, team1, team2, team1wins, team2wins):
    m = []
    i = 0
    while i < pointsPerWeek:
        while team1wins > 0:
            m.append([date, team1, team2, "1-0"])
            team1wins -= 1
            i += 1
        while team2wins > 0:
            m.append([date, team1, team2, "0-1"])
            team2wins -= 1
            i += 1
        if i < pointsPerWeek:
            m.append([date, team1, team2, "0-0"])
            i += 1
    return m


def genFutureMatches(date, team1, team2):
    m = []
    i = 0
    while i < pointsPerWeek:
        m.append([date, team1, team2, "   "])
        i += 1
    return m


def validateMatches(matches, teams):
    for t in teams:
        c = 0
        for row in matches:
            if t in row[1]:
                c += 1
                continue
            if t in row[2]:
                c += 1
        if c != (numWeeks * pointsPerWeek):
            print("team " + t + " has incorrect match count " + str(c))
            exit(1)


def writeFile(teams, matches, file):
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    j2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(THIS_DIR))
    text = j2_env.get_template("template.j2").render(
        teams=teams,
        matches=matches
    )
    try:
        fh = open(file, "w")
        fh.write(text)
        fh.close()
    except:
        print("cloud not write to " + file)
        exit(1)
    print("\n email body written to " + file)


def main():
    outfile = "output_{:%Y%m%d-%H%M%S}".format(datetime.datetime.now())
    schedule = readSchedule(scheduleFile)
    teams = extractTeams(schedule)
    matches = generateMatches(schedule)
    writeFile(teams, matches, outfile)

if __name__ == "__main__":
    main()
