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
matchesPerWeek = 12


def readSchedule(file):
    try:
        fh = open(file, 'r')
    except:
        print("cannot open " + file)
        exit(1)
    reader = csv.reader(filter(lambda row: row[0] != '#', fh))
    schedule = []
    for row in reader:
        if len(row) not in [3, 5]:
            print("bad row in " + file + ' ' + str(row))
            exit(1)
        schedule.append(row)
    fh.close()
    return schedule


def extractTeams(schedule):
    teams = []
    for row in schedule:
        if row[1] not in teams:
            teams.append(row[1])
        if row[2] not in teams:
            teams.append(row[2])
    if len(teams) != numTeams:
        print(sorted(teams))
        print(str(len(teams)) + " not equal " + str(numTeams))
        exit(1)
    for t in teams:
        if len(t) > maxTeamName:
            print(t + " exceeds max length " + str(maxTeamName))
            exit(1)
    return teams


def generateMatches(schedule):
    matches = []
    ties = 0
    wins = 0
    for row in schedule:
        date = row[0]
        team1 = row[1]
        team2 = row[2]
        if len(row) < 5:
            for m in genFutureMatches(date, team1, team2):
                matches.append(m)
        else:
            team1wins = int(row[3])
            team2wins = int(row[4])
            wins += team1wins + team2wins
            ties += matchesPerWeek - team1wins - team2wins
            for m in genPastMatches(date, team1, team2, team1wins, team2wins):
                matches.append(m)
    tiepct = round(ties / wins, 2)
    return matches, tiepct


def genPastMatches(date, team1, team2, team1wins, team2wins):
    matches = []
    i = 0
    while i < matchesPerWeek:
        while team1wins > 0:
            matches.append([date, team1, team2, "1-0"])
            team1wins -= 1
            i += 1
        while team2wins > 0:
            matches.append([date, team1, team2, "0-1"])
            team2wins -= 1
            i += 1
        if i < matchesPerWeek:
            matches.append([date, team1, team2, "0-0"])
            i += 1
    return matches


def genFutureMatches(date, team1, team2):
    matches = []
    i = 0
    while i < matchesPerWeek:
        matches.append([date, team1, team2, "   "])
        i += 1
    return matches


def validateMatches(matches, teams):
    for t in teams:
        c = 0
        for row in matches:
            if t in row[1]:
                c += 1
                continue
            if t in row[2]:
                c += 1
        if c != (numWeeks * matchesPerWeek):
            print("team " + t + " has incorrect match count " + str(c))
            exit(1)


def writeFile(teams, matches, tiepct, file):
    PWD = os.path.dirname(os.path.abspath(__file__))
    j2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(PWD))
    text = j2_env.get_template(mailTemplate).render(
        teams=teams,
        matches=matches,
        tiepct=tiepct)
    try:
        fh = open(file, 'w')
        fh.write(text)
        fh.close()
    except:
        print("could not write to " + file)
        exit(1)
    print("\n email body written to " + file)


def main():
    outfile = "output_{:%Y%m%d-%H%M%S}".format(datetime.datetime.now())
    schedule = readSchedule(scheduleFile)
    teams = extractTeams(schedule)
    matches, tiepct = generateMatches(schedule)
    writeFile(teams, matches, tiepct, outfile)

if __name__ == "__main__":
    main()
