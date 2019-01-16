import numpy as np
import csv
import codecs
import copy
import sys
import xml

index_dict = dict()

giver_index = 3
receiver_index = 4

def is_giver(response):
    return response[giver_index] == "Yes"

def is_receiver(response):
    return response[receiver_index] == "Yes"

def make_match(giver, receiver, match_type):
    match = []
    match.append(giver[index_dict["Discord username"]])
    match.append(receiver)
    match.append(match_type)

    return match

def make_matches(givers, receivers, match_type):
    good_matches = False
    matches = []
    leftovers = []
    while not good_matches:
        nb_matches = min(len(givers), len(receivers))
        matches = []
        good_matches = True
        for k in range(0, nb_matches):
            if givers[k][2] == receivers[k][2]:
                #don't gift to yourself
                good_matches = False
                receivers += [receivers[0]]
                receivers.pop(0)
                break
            match = make_match(givers[k], receivers[k], match_type)
            matches.append(match)

    #leftovers still have to give and receive
    if(len(givers) > nb_matches):
        receivers += givers[nb_matches:]
    elif len(receivers) > nb_matches:
        givers += receivers[nb_matches:]

    return matches

def match_both(responses, match_type):
    np.random.shuffle(responses)
    #cycle by 1 the vector
    responses2 = copy.deepcopy(responses)
    responses2 += [responses2[0]]
    responses2.pop(0)
    matches = make_matches(responses, responses2, match_type)
    return matches

def load_data(filename):
    responses = []
    types_of_encoding = ["utf8"]
    for encoding_type in types_of_encoding:
        with codecs.open(filename, encoding = encoding_type, errors ='replace') as responsefile:
            reader = csv.reader(responsefile, delimiter='\t', quotechar='"')
            for row in reader:
                responses.append(row)

    return responses[0], responses[1:]

def process(responses):

    #Find physical both giver and senders
    both = []
    givers = []
    receivers = []

    #only digital
    neither = []

    for r in responses:
        if is_giver(r):
            if is_receiver(r):
                both.append(r)
            else:
                givers.append(r)
        else:
            if is_receiver(r):
                receivers.append(r)
            else:
                neither.append(r)

    matches = match_both(both, "physical")
    np.random.shuffle(givers)
    np.random.shuffle(receivers)
    tmp_matches = make_matches(givers, receivers, "physical")
    matches += tmp_matches

    #only givers have to be receivers too and vice-versa
    neither_giver = copy.deepcopy(neither)
    neither_giver += receivers
    neither_receiver = copy.deepcopy(neither)
    neither_receiver += givers
    np.random.shuffle(neither_giver)
    np.random.shuffle(neither_receiver)
    tmp_matches = make_matches(neither_giver, neither_receiver, "digital")
    matches += tmp_matches
    return matches


def make_index_dict(titles):
    for k in range(0, len(titles)):
        index_dict[titles[k]] = k

def make_address(person):
    string = person[index_dict["Name"]].replace('\r\n', '') + "\n"
    string += person[index_dict["Address Line 1"]].replace('\r\n', '')  + "\n"
    line2 = person[index_dict["Adress Line 2"]].replace('\r\n', '')
    if(line2 != ""):
        string += line2 + "\n"
    state = person[index_dict["State"]].replace('\r\n', '')
    if(state != ""):
        string += state + "\n"
    string += person[index_dict["Zip/Postal Code"]].replace('\r\n', '')  + " "
    string += person[index_dict["City"]].replace('\r\n', '')  + "\n"
    string += person[index_dict["Country"]].replace('\r\n', '')  + "\n"
    return string

def make_gift_info(person):
    string = "**Who's your bias in SNSD ?**" + "\n" + person[index_dict["Who's your bias in SNSD (including Jessica you smartass)?"]] + "\n\n"
    string += "**What other kpop group do you like?**" + "\n" + person[index_dict["What other kpop group do you like?"]] + "\n\n"
    string += "**Who are your favorite idols in general ?**" + "\n" + person[index_dict["Who are your favorite idols in general (including IU you smartass)?"]] + "\n\n"
    string += "**Who are your other favorite actors? Singers? Entertainers?**" + "\n" + person[index_dict["Who are your other favorite actors? Singers? Entertainers?"]] + "\n\n"
    string += "**What is your favorite TV show or movie?**" + "\n" + person[index_dict["What is your favorite TV show or movie?"]] + "\n\n"
    string += "**What are your favorite foods?**" + "\n" + person[index_dict["What are your favorite foods?"]] + "\n\n"
    string += "**What are your allergies?**" + "\n" + person[index_dict["What are your allergies?"]] + "\n\n"
    string += "**What's your t-shirt size?**" + "\n" + person[index_dict["What's your t-shirt size? (please make sure to specify the type of size you are referring to, e.g. \"XXXXL US\")"]] + "\n\n"
    string += "**What are your favorite books or authors?**" + "\n" + person[index_dict["What are your favorite books or authors?"]] + "\n\n"
    string += "**Notes to help your Santa:**" + "\n" + person[index_dict["Notes to help your Santa:"]] + "\n\n"
    return string


def make_pretty_easylife_file(matches):

    summary = open("summary.txt", 'w', encoding="utf-8")

    for m in matches:
        giver =  m[0]
        file = open("matches\\" + giver + ".txt", 'w', encoding="utf-8")
        receiver = m[1]
        string = "Hey! Your *My Sone Secret Santa* match is here!\nYou will be sending a gift to " + receiver[2] + "\n"
        if m[2] == "physical":
            string += "They agreed to receive a physical gift, their address is: \n"
            string += make_address(receiver) + "\n"
            string += "Please keep in mind that this address is not to be shared with anyone!\n"
            string += "Please try to write the address according to the destination country's format to ensure a smooth ride for your gift.\n\n"

        else :
            string += "They agreed to receive a digital gift. \n\n"

        string += "Below is their answers to some questions to help you find an amazing gift. \n\n"
        string += make_gift_info(receiver)

        string += "Please note that this is not the same person you will receive a gift from! \nGood Luck!\n\n"
        string += "PS: if you have any question, feel free to message me!"

        string.encode('UTF-8')
        file.write(string)
        summary.write(giver + " sends " + m[2] + " to " + receiver[2] + "\n")

def make_DOT(matches):
    #to visualise as a cute graph
    string = "digraph secretsanta {\n"
    for m in matches:
        receiver = m[1][2].replace(' ', '')
        giver =  m[0].replace(' ', '')
        string += "\"" + giver + "\" -> \"" + receiver + "\";\n"

    string += "}"
    dotFile = open("graph.dot", 'w', encoding="utf-8")
    dotFile.write(string)

if __name__ == "__main__":
    titles, responses = load_data("responses.tsv")
    make_index_dict(titles)
    matches = process(responses)
    make_pretty_easylife_file(matches)
    make_DOT(matches)
    print(responses)
