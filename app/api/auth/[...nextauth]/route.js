import NextAuth from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';
import User from '@models/user';
import { connectToDB } from '@utils/database';

const handler = NextAuth({
    providers: [
        GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET,
            authorization: {
                params: {
                    prompt: "consent",
                    access_type: "offline",
                    response_type: "code",
                }
            }
        })
    ],
    callbacks: {
        async session({ session }) {
            await connectToDB(); // Ensure DB connection

            const sessionUser = await User.findOne({ email: session.user.email });
            session.user.id = sessionUser?._id.toString(); // Using optional chaining for safety
            return session;
        },
        async signIn({ profile }) {
            try {
                await connectToDB(); // Ensure DB connection

                // Check if the user already exists in the database
                const userExists = await User.findOne({ email: profile.email });

                // If the user does not exist, create a new user
                if (!userExists) {
                    await User.create({
                        email: profile.email,
                        username: profile.name.replace(" ", "").toLowerCase(),
                        image: profile.picture,
                    });
                }
                return true;
            } catch (error) {
                console.log("Error in signIn callback:", error);
                return false;
            }
        }
    }
});

export { handler as GET, handler as POST };
