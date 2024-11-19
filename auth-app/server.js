const express = require("express");
const mongoose = require("mongoose");
const bcrypt = require("bcryptjs");
const cors = require("cors");
const app = express();
const port = 3001;

// Enable CORS
app.use(cors());

// MongoDB connection
mongoose.connect("mongodb://127.0.0.1:27017/authDB", { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log("Connected to MongoDB"))
    .catch((error) => console.error("MongoDB connection error:", error));

// User schema
const userSchema = new mongoose.Schema({
    email: { type: String, unique: true, required: true },
    password: { type: String, required: true }
});

const User = mongoose.model("User", userSchema);

// Middleware to parse JSON data
app.use(express.json());

// Sign-up endpoint
app.post("/signup", async (req, res) => {
    const { email, password } = req.body;

    try {
        const userExists = await User.findOne({ email });
        if (userExists) {
            return res.status(400).json({ error: "User already exists" });
        }

        // Hash password
        const hashedPassword = await bcrypt.hash(password, 10);
        const newUser = new User({ email, password: hashedPassword });

        await newUser.save();
        res.status(200).json({ message: "Sign up successful" });
    } catch (error) {
        res.status(500).json({ error: "Internal server error" });
    }
});

// Login endpoint
app.post("/login", async (req, res) => {
    const { email, password } = req.body;

    try {
        const user = await User.findOne({ email });
        if (!user) {
            return res.status(400).json({ error: "Invalid email or password" });
        }

        // Debugging: Log the stored hashed password
        console.log("Stored hashed password:", user.password);

        // Compare password with hashed password in the database
        const isPasswordCorrect = await bcrypt.compare(password, user.password);

        // Debugging: Log the result of bcrypt comparison
        console.log("Password comparison result:", isPasswordCorrect);

        if (!isPasswordCorrect) {
            return res.status(400).json({ error: "Invalid email or password" });
        }

        // Successful login
        res.status(200).json({ message: "Login successful" });
    } catch (error) {
        res.status(500).json({ error: "Internal server error" });
    }
});

// Start the server
app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
