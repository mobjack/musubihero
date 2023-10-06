import os
import sys
import json
import time
import socket
import imaplib
import pendulum
import traceback
import datetime as dt
import shortuuid
import email_corrector as ec

from logit import logit
from jprint import jprint
from copy import deepcopy
from random import randint
from logit import my_exception_hook
from BayesClassifier import junknotjunk
from BayesClassifier import bayes_training as bayes
from imap_tools import A, AND, MailBox, MailboxLoginError, MailboxLogoutError


class Ecrawler:
    def __init__(self, uAccount, musubi_junk="musubi-junk", musubi_ok="musubi-ok"):
        restart_login_hours = 2
        self.restart_login_seconds = restart_login_hours * 3600
        self.uAccount = uAccount
        self.jnk = junknotjunk(uAccount["musubi_id"])
        now = self._getnow()
        self.today = dt.datetime.now().date()
        self.todays_email_ids = []
        self.uAccount.update(
            {
                "folders": {
                    musubi_junk: now,
                    musubi_ok: now,
                    "musubi-scored": now,
                    uAccount["inbox"]: now,
                    uAccount["spambox"]: now,
                }
            }
        )
        self.dontcheckfolders = ["Junk", "[Gmail]/Spam", "musubi-scored"]
        self.msg_db = []
        self.msg_file = str(f'../data/{self.uAccount["email"]}.json').replace("@", "__")
        self._mb_login()

        #self.mb = MailBox(self.uAccount["imap_url"]).login(
        #    self.uAccount["email"], self.uAccount["cred"]
        #)

        self.user_folders = []
        for ufolder in self.uAccount["folders"]:
            is_exists = self.mb.folder.exists(ufolder)

            if is_exists == False and ufolder.startswith("musubi"):
                print(f"Creating folder {ufolder}")
                self.mb.folder.create(ufolder)
            elif is_exists == False:
                raise ValueError(
                    f"Cannot find folder {ufolder} in {self.uAccount['email']}"
                )
            else:
                pass
            self.user_folders.append(ufolder)

    def _mb_login(self):
        print(f'Connecting to Account {self.uAccount["email"]}')
        self.mb = MailBox(self.uAccount["imap_url"]).login(
            self.uAccount["email"], self.uAccount["cred"]
        )

    def get_training(self, daysback=120):
        daystosearch = pendulum.now().subtract(days=daysback)
        sd = pendulum.datetime(daystosearch.year, daystosearch.month, daystosearch.day)
        ed = pendulum.today()
        period = pendulum.period(sd, ed)
        pulldates = []
        for mydt in period.range("months"):
            dt_end_month = mydt.end_of("month")
            pulldates.append(
                [
                    (mydt.year, mydt.month, 1),
                    (dt_end_month.year, dt_end_month.month, dt_end_month.day),
                ]
            )

        for foldername in self.uAccount["folders"]:
            self.mb.folder.set(foldername)
            if str(foldername).lower() not in ("inbox", "musubi-ok"):
                junk_text = "junk"
                junk_bool = True
            else:
                junk_text = "ok"
                junk_bool = False

            for tdate in pulldates:
                s_yr = tdate[0][0]
                s_mo = tdate[0][1]
                s_day = 1

                e_yr = tdate[1][0]
                e_mo = tdate[1][1]
                e_day = tdate[1][2]

                for date_emails in self.mb.fetch(
                    criteria=AND(
                        date_gte=dt.date(s_yr, s_mo, s_day),
                        date_lt=dt.date(e_yr, e_mo, e_day),
                    ),
                    mark_seen=False,
                    bulk=True,
                ):
                    fixed_email = self._norm_email(date_emails)  # returns dict
                    if fixed_email == None:  # not a good training email
                        continue

                    fixed_email.update(
                        {
                            "folder": foldername,
                            "junktext": junk_text,
                            "junk_bool": junk_bool,
                        }
                    )

                    self.msg_db.append(fixed_email)

        with open(self.msg_file, "w") as account_file:
            json.dump(self.msg_db, account_file)

    def monitor_mailbox(self):
        print("monitor-->", self.uAccount["email"])

        while True:
            monitor_now = self._getnow()
            restart_time = monitor_now + self.restart_login_seconds
            
            if monitor_now > restart_time: # login again after x time
                self._mb_login()

            for mfolder, last_check in self.uAccount["folders"].items():
                # if mfolder == 'Junk' or mfolder == '[Gmail]/Spam':
                if mfolder in self.dontcheckfolders:
                    continue

                if monitor_now - last_check >= 60:  # one minute
                    print("-->folder check", self.uAccount["email"], mfolder)
                    self.mb.folder.set(mfolder)
                    # if mfolder == 'musubi-junk':
                    if str(mfolder).startswith("musubi-"):
                        # pull all msgs
                        monitor_messages = self._fetch_mail(
                            "all", self.uAccount["email"], mfolder
                        )

                        if monitor_messages == None:
                            self.uAccount["folders"][mfolder] = monitor_now
                            continue

                        mjunk = []
                        update_check = False
                        for monitor_msg in monitor_messages:  # fetch all msgs
                            musubi_jemail = deepcopy(monitor_msg)

                            if mfolder == "musubi-junk":
                                musubi_jemail.update(
                                    {
                                        "junktext": "junk",
                                        "junk_bool": True,
                                        "folder": "moved2junk",
                                    }
                                )
                            else:
                                musubi_jemail.update(
                                    {
                                        "junktext": "ok",
                                        "junk_bool": False,
                                        "folder": "moved2inbox",
                                    }
                                )

                            logmsg = {
                                "loglevel": "info",
                                "name": "Junk email moved",
                                "info": {
                                    "folder": mfolder,
                                    "account": self.uAccount["email"],
                                    "count": 1,
                                    "eid": musubi_jemail["eid"],
                                    "subject": musubi_jemail["subject"],
                                    "to": musubi_jemail["to"],
                                    "from": musubi_jemail["from"],
                                },
                            }
                            logit(logmsg)

                            mjunk.append(musubi_jemail)
                            update_check = True

                        if update_check == True:
                            self.update_msg_db(mjunk)

                            # re-create all pkl files
                            with open(
                                f"../data/{self.uAccount['musubi_id']}.json"
                            ) as udf:
                                new_msg_db = json.load(udf)
                            bayes(new_msg_db)  # retrain

                            if mfolder == "musubi-junk":
                                print("moving emails to scored")
                                self.mb.move(self.mb.uids(), "musubi-scored")
                            else:  # move back to inbox
                                print(f"moving emails to {self.uAccount['inbox']}")
                                self.mb.move(self.mb.uids(), self.uAccount["inbox"])

                    # SCORING HERE
                    else:
                        new_emails = self._fetch_mail(
                            "monitor", self.uAccount["email"], mfolder
                        )

                        if new_emails == None:
                            self.uAccount["folders"][mfolder] = monitor_now
                            continue

                        for new_msg in new_emails:
                            # norm_new_msg = self._norm_email(new_msg, training=False)
                            is_isnot_junk = self.jnk.get_junk_stats(new_msg)
                            print(new_msg)
                            #print(is_isnot_junk)
                            print("--------")
                            logmsg = {
                                "loglevel": "info",
                                "name": "Scored Email",
                                "info": {
                                    "folder": mfolder,
                                    "account": self.uAccount["email"],
                                    "count": 1,
                                    "eid": new_msg["eid"],
                                    "subject": new_msg["subject"],
                                    "to": new_msg["to"],
                                    "scores": is_isnot_junk,
                                },
                            }
                            logit(logmsg)
                            if is_isnot_junk["is_junk"] == True:
                                self.mb.move(new_msg["sid"], "musubi-scored")
                            # print('->', monitor_msg.date, monitor_msg.subject)
                    self.uAccount["folders"][mfolder] = monitor_now
                    continue
                else:
                    rando_sleep = randint(8, 15)
                    time.sleep(rando_sleep)

    def _fetch_mail(self, fetch_type, account, afolder):
        self.mb.folder.set(afolder)
        sys.excepthook = my_exception_hook
        new_msg_list = []

        if self.today != dt.datetime.now().date():
            self.today = dt.datetime.now().date()
            self.todays_email_ids = []  # reset today's ids

        if fetch_type == "monitor":
            # new_emails = self.mb.fetch(A(recent=True), mark_seen=False)
            # new_emails = self.mb.fetch(A(new=True), mark_seen=False)
            new_emails = self.mb.fetch(
                criteria=AND(date_gte=self.today), mark_seen=False, bulk=True
            )

        else:  # fetch all
            new_emails = self.mb.fetch()

        email_count = 0
        if new_emails:
            for email_trk in new_emails:
                if fetch_type == "monitor":
                    if email_trk.uid not in self.todays_email_ids:
                        new_msg_list.append(self._norm_email(email_trk, training=False))
                        self.todays_email_ids.append(email_trk.uid)
                else:
                    new_msg_list.append(self._norm_email(email_trk, training=False))
                email_count += 1

            if email_count == 0:
                return None

            logmsg = {
                "loglevel": "info",
                "name": "new emails found",
                "info": {"folder": afolder, "account": account, "count": email_count},
            }
            #logit(logmsg)
            return new_msg_list
        else:
            return None

    def get_filename(self):
        return self.msg_file

    def update_msg_db(self, msg_list):
        user_db_file = f"../data/{self.uAccount['musubi_id']}.json"
        with open(user_db_file, "r") as umdb:
            msg_db_list = json.load(umdb)

        msg_db_list.extend(msg_list)

        with open(user_db_file, "w") as newdb:
            json.dump(msg_db_list, newdb, indent=2)

    def _norm_email(self, pulld_email_data, training=True):
        msg_dict = {}
        fix_body = ec.clean_body(pulld_email_data.text)
        fix_sub = ec.clean_body(pulld_email_data.subject, bodytype="subject")

        if training == True:
            if fix_body == None or fix_sub == None:
                return None

        msg_dict = {
            "eid": shortuuid.uuid(),
            "aid": self.uAccount["musubi_id"],
            "sid": pulld_email_data.uid,
            "from": ec.lcase_email(pulld_email_data.from_),
            "to": ec.lcase_email(pulld_email_data.to),
            "replyto": ec.lcase_email(pulld_email_data.reply_to),
            "ts": ec.fix_ts(pulld_email_data.date),
            "urls": ec.find_urls(pulld_email_data.text),
            "subject": fix_sub,
            "body": fix_body,
        }
        return msg_dict

    def _getnow(self):
        return int(pendulum.now().format("X"))
