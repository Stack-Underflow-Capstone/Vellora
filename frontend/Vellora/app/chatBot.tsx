import { View, Text, Image, TextInput, Pressable, StyleSheet, StatusBar, ScrollView, Animated, Alert } from "react-native";
import { router } from "expo-router";
import { FontAwesome } from "@expo/vector-icons";
import { useState, useEffect, useRef } from "react";
import { askTripAssistant } from "./services/ai";
import { ApiError } from "./services/helpers";

type Message = {
	id: string;
	text: string;
	isUser: boolean;
	timestamp: Date;
};

export default function ChatBot() {
	const [messages, setMessages] = useState<Message[]>([]);
	const [inputText, setInputText] = useState('');
	const [isTyping, setIsTyping] = useState(false);
	const scrollViewRef = useRef<ScrollView>(null);

	useEffect(() => {
		if (messages.length > 0) {
			setTimeout(() => {
				scrollViewRef.current?.scrollToEnd({ animated: true });
			}, 100);
		}
	}, [messages]);

	const sendMessage = async () => {
		if (inputText.trim() === '') return;

		const newMessage: Message = {
			id: Date.now().toString(),
			text: inputText,
			isUser: true,
			timestamp: new Date()
		};

		setMessages(prev => [...prev, newMessage]);
		const currentInput = inputText;
		setInputText('');
		setIsTyping(true);

		try {
			const response = await askTripAssistant(currentInput);
			
			const botMessage: Message = {
				id: Date.now().toString() + '_bot',
				text: response.assistant_message,
				isUser: false,
				timestamp: new Date()
			};
			
			setIsTyping(false);
			setMessages(prev => [...prev, botMessage]);
		} catch (error) {
			setIsTyping(false);
			
			let errorMessage = "Sorry, I'm having trouble connecting right now. Please try again.";
			
			if (error instanceof ApiError) {
				if (error.status === 401) {
					errorMessage = "Please log in to continue chatting.";
					Alert.alert("Login Required", "You need to be logged in to use the chat assistant.", [
						{ text: "OK", onPress: () => router.push('/login') }
					]);
					return;
				} else {
					errorMessage = error.message || errorMessage;
				}
			}
			
			const errorBotMessage: Message = {
				id: Date.now().toString() + '_error',
				text: errorMessage,
				isUser: false,
				timestamp: new Date()
			};
			
			setMessages(prev => [...prev, errorBotMessage]);
		}
	};

	//typinh animation
	const TypingIndicator = () => {
		const dot1 = useRef(new Animated.Value(0)).current;
		const dot2 = useRef(new Animated.Value(0)).current;
		const dot3 = useRef(new Animated.Value(0)).current;

		useEffect(() => {
			const animate = () => {
				const animateDot = (dot: Animated.Value, delay: number) => {
					return Animated.loop(
						Animated.sequence([
							Animated.delay(delay),
							Animated.timing(dot, {
								toValue: 1,
								duration: 400,
								useNativeDriver: true,
							}),
							Animated.timing(dot, {
								toValue: 0,
								duration: 400,
								useNativeDriver: true,
							}),
						])
					);
				};

				Animated.parallel([
					animateDot(dot1, 0),
					animateDot(dot2, 200),
					animateDot(dot3, 400),
				]).start();
			};

			animate();
		}, [dot1, dot2, dot3]);

		return (
			<View style={styles.messageContainer}>
				<View style={styles.botMessage}>
					<View style={[styles.messageBubble, styles.botBubble, styles.typingBubble]}>
						<View style={styles.typingContainer}>
							<Animated.View style={[styles.typingDot, { opacity: dot1 }]} />
							<Animated.View style={[styles.typingDot, { opacity: dot2 }]} />
							<Animated.View style={[styles.typingDot, { opacity: dot3 }]} />
						</View>
					</View>
				</View>
			</View>
		);
	};

	return (
		<View style={styles.container}>
			<StatusBar barStyle="light-content" backgroundColor="#404CCF" />
			<View style={styles.header}>
				<Pressable onPress={() => router.back()} style={styles.backButton}>
					<FontAwesome name="chevron-left" size={20} color="#FFFFFF" />
				</Pressable>
				<Text style={styles.headerTitle}>Velo</Text>
				<View style={styles.headerSpacer} />
			</View>

			<ScrollView 
				ref={scrollViewRef}
				style={styles.messagesContainer}
				contentContainerStyle={styles.messagesContent}
				showsVerticalScrollIndicator={false}
			>
				<View style={styles.mascotContainer}>
					<Image 
						source={require("./assets/velo.png")} 
						style={styles.mascotImage} 
						resizeMode="contain"
					/>
					<Image source={require("./assets/wheel.png")} style={styles.wheelTop} />
					<Image source={require("./assets/wheel.png")} style={styles.wheelBottomLeft} />
					<Image source={require("./assets/wheel.png")} style={styles.wheelBottomRight} />
				</View>

				{messages.map((message) => (
					<View key={message.id} style={[
						styles.messageContainer,
						message.isUser ? styles.userMessage : styles.botMessage
					]}>
						<View style={[
							styles.messageBubble,
							message.isUser ? styles.userBubble : styles.botBubble
						]}>
							<Text style={[
								styles.messageText,
								message.isUser ? styles.userText : styles.botText
							]}>
								{message.text}
							</Text>
						</View>
					</View>
				))}

				{isTyping && <TypingIndicator />}
			</ScrollView>

			<View style={styles.inputContainer}>
				<View style={styles.inputWrapper}>
					<TextInput
						style={styles.textInput}
						placeholder="Ask your question..."
						placeholderTextColor="#999"
						multiline
						value={inputText}
						onChangeText={setInputText}
						onSubmitEditing={sendMessage}
					/>
					<Pressable style={styles.sendButton} onPress={sendMessage}>
						<View style={styles.sendIconContainer}>
							<View style={styles.linesContainer}>
								<View style={styles.line1} />
								<View style={styles.line2} />
								<View style={styles.line3} />
							</View>
							<Image source={require("./assets/wheel.png")} style={styles.wheelBackground} />
						</View>
					</Pressable>
				</View>
			</View>
		</View>
	);
}

const styles = StyleSheet.create({
	container: {
		flex: 1,
		backgroundColor: "#131313",
	},
	header: {
		flexDirection: "row",
		alignItems: "center",
		paddingHorizontal: 20,
		paddingVertical: 15,
		paddingTop: 50,
		backgroundColor: "#404CCF",
	},
	backButton: {
		width: 40,
		height: 40,
		justifyContent: "center",
		alignItems: "flex-start",
	},
	headerTitle: {
		flex: 1,
		textAlign: "center",
		fontSize: 25 ,
		fontWeight: "600",
		color: "#FFFFFF",
	},
	headerSpacer: {
		width: 40,
	},
	messagesContainer: {
		flex: 1,
		backgroundColor: "#131313",
	},
	messagesContent: {
		padding: 20,
		paddingBottom: 10,
	},
	content: {
		flex: 1,
		position: "relative",
		justifyContent: "center",
		alignItems: "center",
	},
	wheelTop: {
		position: "absolute",
		top: 50,
		right: 0,
		width: 90,
		height: 90,
		zIndex: 10,
	},
	wheelBottomLeft: {
		position: "absolute",
		bottom: 80,
		left: 20,
		width: 70,
		height: 70,
		zIndex: 10,
	},
	wheelBottomRight: {
		position: "absolute",
		bottom: 55,
		left: 90,
		width: 50,
		height: 50,
		zIndex: 10,
	},
	mascotContainer: {
		alignItems: "center",
		justifyContent: "center",
	},
	mascotImage: {
		width: 500,
		height: 500,
	},
	messageContainer: {
		marginVertical: 4,
		paddingHorizontal: 10,
	},
	userMessage: {
		alignItems: "flex-end",
	},
	botMessage: {
		alignItems: "flex-start",
	},
	messageBubble: {
		maxWidth: "80%",
		paddingHorizontal: 16,
		paddingVertical: 12,
		borderRadius: 18,
	},
	userBubble: {
		backgroundColor: "#44A65C",
		borderBottomRightRadius: 4,
	},
	botBubble: {
		backgroundColor: "#B8D9C0",
		borderBottomLeftRadius: 4,
	},
	messageText: {
		fontSize: 16,
		lineHeight: 20,
	},
	userText: {
		color: "#F2F2F2",
	},
	botText: {
		color: "#032A0C",
	},
	inputContainer: {
		paddingHorizontal: 23,
		paddingBottom: 25,
		paddingTop: 10,
		marginBottom: 10
	},
	inputWrapper: {
		flexDirection: "row",
		alignItems: "flex-end",
		backgroundColor: "#272727",
		borderRadius: 15,
		paddingHorizontal: 15,
		paddingVertical: 5,
	},
	textInput: {
		flex: 1,
		color: "#FFFFFF",
		fontSize: 16,
		maxHeight: 100,
		paddingVertical: 8,
	},
	sendButton: {
		width: 30,
		height: 25,
		borderRadius: 0,
		justifyContent: "center",
		alignItems: "center",
		padding: 5,
		marginBottom: 6,
		right: 5
	},
	sendIconContainer: {
		width: 40,
		height: 25,
		justifyContent: "center",
		alignItems: "center",
		flexDirection: "row",
	},
	wheelBackground: {
		width: 20,
		height: 20,
	},
	linesContainer: {
		justifyContent: "space-around",
		alignItems: "flex-end",
		marginRight: 3,
		height: 12,
		flexDirection: "column",
	},
	line1: {
		width: 15,
		height: 1,
		backgroundColor: "#4DBF69",
		marginBottom: 2,
	},
	line2: {
		width: 10,
		height: 1,
		backgroundColor: "#4DBF69",
		marginBottom: 2,
	},
	line3: {
		width: 5,
		height: 1,
		backgroundColor: "#4DBF69",
	},
	typingBubble: {
		paddingHorizontal: 20,
		paddingVertical: 16,
	},
	typingContainer: {
		flexDirection: "row",
		alignItems: "center",
		justifyContent: "center",
	},
	typingDot: {
		width: 8,
		height: 8,
		borderRadius: 4,
		backgroundColor: "#032A0C",
		marginHorizontal: 2,
	},
});