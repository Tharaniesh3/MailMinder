import 'dart:js';

import 'package:flutter/material.dart';
import 'package:googleapis/gmail/v1.dart' as gmail;
import 'package:googleapis_auth/auth_io.dart' as auth;
import 'package:google_sign_in/google_sign_in.dart';
import 'package:http/http.dart' as http;

final String clientId = 'YOUR_CLIENT_ID';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Gmail API Demo',
      home: GmailAuthScreen(),
    );
  }
}

class GmailAuthScreen extends StatelessWidget {
  static const List<String> scopes = [gmail.GmailApi.gmailReadonlyScope];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Gmail Authentication')),
      body: Center(
        child: ElevatedButton(
          onPressed: () async {
            final credentials = await obtainCredentials(scopes);
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => GmailEmailsScreen(credentials: credentials),
              ),
            );
          },
          child: Text('Authenticate with Gmail'),
        ),
      ),
    );
  }
}

Future<auth.AccessCredentials> obtainCredentials(List<String> scopes) async {
  final googleSignIn = GoogleSignIn(scopes: scopes);

  try {
    final googleSignInAccount = await googleSignIn.signIn();

    if (googleSignInAccount == null) {
      throw Exception('Google Sign-In was canceled.');
    }

    final googleSignInAuthentication = await googleSignInAccount.authentication;
    final authClient = await auth.clientViaUserConsent(
      auth.ClientId(clientId, ''),
      scopes,
      auth.UserConsent.prompt(context),
      code: googleSignInAuthentication.serverAuthCode,
    );

    final accessCredentials = await authClient.credentials;

    return accessCredentials;
  } catch (e) {
    print('Error during Google Sign-In: $e');
    rethrow;
  }
}

class GmailEmailsScreen extends StatefulWidget {
  final auth.AccessCredentials credentials;

  GmailEmailsScreen({required this.credentials});

  @override
  _GmailEmailsScreenState createState() => _GmailEmailsScreenState();
}

class _GmailEmailsScreenState extends State<GmailEmailsScreen> {
  List<gmail.Message>? _emails;

  @override
  void initState() {
    super.initState();
    fetchEmails();
  }

  Future<void> fetchEmails() async {
    final client = http.Client();
    final authenticatedClient = auth.authenticatedClient(
      client,
      widget.credentials,
    );

    try {
      final gmailApi = gmail.GmailApi(authenticatedClient);
      final listMessages = await gmailApi.users.messages.list('me');

      setState(() {
        _emails = listMessages.messages;
      });
    } catch (e) {
      print('Error fetching emails: $e');
    } finally {
      client.close();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Gmail Emails')),
      body: ListView.builder(
        itemCount: _emails?.length ?? 0,
        itemBuilder: (context, index) {
          final email = _emails![index];
          return ListTile(
            title: Text(email.id ?? ''),
            subtitle: Text(email.snippet ?? ''),
            onTap: () async {
              final client = http.Client();
              final authenticatedClient = auth.authenticatedClient(
                client,
                widget.credentials,
              );

              try {
                final gmailApi = gmail.GmailApi(authenticatedClient);
                final message = await gmailApi.users.messages.get('me', email.id!);

                // Process the message and display it in your app's UI.
                // The variable `message` contains the full content and details of the selected email.
                print('Email Subject: ${message?.payload?.headers?.firstWhere((h) => h.name == 'Subject', orElse: () => gmail.MessagePartHeader(name: 'Subject', value: ''))?.value ?? ''}');
              } catch (e) {
                print('Error fetching email message: $e');
              } finally {
                client.close();
              }
            },
          );
        },
      ),
    );
  }
}
